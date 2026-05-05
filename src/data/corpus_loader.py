"""Data loading and processing utilities"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from src.core.logger import get_logger

logger = get_logger(__name__)


class CorpusLoader:
    """Load SAS code corpus from files"""

    def __init__(self, corpus_path: Path):
        self.corpus_path = Path(corpus_path)
        self.corpus_path.mkdir(parents=True, exist_ok=True)

    def load_corpus(self) -> List[Dict[str, str]]:
        """Load all SAS files from corpus directory"""
        sas_files = list(self.corpus_path.glob("*.sas"))
        logger.info(f"Found {len(sas_files)} SAS files")

        corpus = []
        for sas_file in sas_files:
            try:
                with open(sas_file, "r", encoding="utf-8") as f:
                    code = f.read()
                    corpus.append(
                        {
                            "id": sas_file.stem,
                            "filename": sas_file.name,
                            "code": code,
                        }
                    )
                logger.debug(f"Loaded: {sas_file.name}")
            except Exception as e:
                logger.error(f"Failed to load {sas_file.name}: {e}")

        return corpus

    def load_metadata(self, metadata_file: Optional[Path] = None) -> Dict:
        """Load metadata for SAS files"""
        if metadata_file is None:
            metadata_file = self.corpus_path.parent / "metadata.json"

        if not metadata_file.exists():
            logger.warning(f"Metadata file not found: {metadata_file}")
            return {}

        try:
            with open(metadata_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return {}


class CodeChunker:
    """Split SAS code into retrieval-friendly chunks."""

    BLOCK_START_RE = re.compile(
        r"^\s*(data\b|proc\s+(sql|sort|means|summary|report|freq|transpose|print|glm|mixed|lifetest)\b|%macro\b)",
        re.IGNORECASE,
    )
    BLOCK_END_RE = re.compile(r"^\s*(run\s*;|quit\s*;|%mend\b.*;)\s*$", re.IGNORECASE)

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_code(self, code: str, code_id: str) -> List[Dict[str, str]]:
        """
        Split code into semantic SAS chunks.

        Primary split points are DATA steps, PROC blocks, and macros. Oversized
        blocks are then split by token count with a small line overlap.
        """
        chunks: List[Dict[str, str]] = []
        for block in self._split_structural_blocks(code):
            chunks.extend(self._split_large_block(block, code_id, len(chunks)))
        return chunks

    def _split_structural_blocks(self, code: str) -> List[Dict[str, str]]:
        """Split SAS into DATA/PROC/macro blocks while preserving setup lines."""
        lines = code.splitlines()
        blocks = []
        current_chunk = []
        start_line = 1
        chunk_type = "preamble"

        for line_number, line in enumerate(lines, start=1):
            starts_new_block = bool(self.BLOCK_START_RE.match(line))

            if starts_new_block and current_chunk:
                blocks.append(
                    {
                        "text": "\n".join(current_chunk).strip(),
                        "start_line": start_line,
                        "end_line": line_number - 1,
                        "chunk_type": chunk_type,
                    }
                )
                current_chunk = []
                start_line = line_number

            if starts_new_block:
                chunk_type = self._classify_block(line)

            current_chunk.append(line)

            if self.BLOCK_END_RE.match(line) and current_chunk:
                blocks.append(
                    {
                        "text": "\n".join(current_chunk).strip(),
                        "start_line": start_line,
                        "end_line": line_number,
                        "chunk_type": chunk_type,
                    }
                )
                current_chunk = []
                start_line = line_number + 1
                chunk_type = "preamble"

        if current_chunk:
            blocks.append(
                {
                    "text": "\n".join(current_chunk).strip(),
                    "start_line": start_line,
                    "end_line": len(lines),
                    "chunk_type": chunk_type,
                }
            )

        return [block for block in blocks if block["text"]]

    def _split_large_block(
        self,
        block: Dict[str, str],
        code_id: str,
        start_index: int,
    ) -> List[Dict[str, str]]:
        """Split an oversized SAS block by token count."""
        chunks = []
        lines = block["text"].splitlines()
        current_chunk = []
        current_tokens = 0
        chunk_start_line = block["start_line"]

        for offset, line in enumerate(lines):
            line_tokens = len(line.split())

            if current_chunk and current_tokens + line_tokens > self.chunk_size:
                chunks.append(
                    self._build_chunk(
                        code_id=code_id,
                        index=start_index + len(chunks),
                        text="\n".join(current_chunk),
                        start_line=chunk_start_line,
                        end_line=block["start_line"] + offset - 1,
                        chunk_type=block["chunk_type"],
                    )
                )
                overlap_lines = max(0, self.overlap // 10)
                current_chunk = current_chunk[-overlap_lines:] if overlap_lines else []
                current_tokens = sum(len(l.split()) for l in current_chunk)
                chunk_start_line = block["start_line"] + offset - len(current_chunk)

            current_chunk.append(line)
            current_tokens += line_tokens

        if current_chunk:
            chunks.append(
                self._build_chunk(
                    code_id=code_id,
                    index=start_index + len(chunks),
                    text="\n".join(current_chunk),
                    start_line=chunk_start_line,
                    end_line=block["end_line"],
                    chunk_type=block["chunk_type"],
                )
            )

        return chunks

    def _build_chunk(
        self,
        code_id: str,
        index: int,
        text: str,
        start_line: int,
        end_line: int,
        chunk_type: str,
    ) -> Dict[str, str]:
        return {
            "id": f"{code_id}_chunk_{index}",
            "code_id": code_id,
            "text": text.strip(),
            "start_line": start_line,
            "end_line": end_line,
            "chunk_type": chunk_type,
        }

    def _classify_block(self, line: str) -> str:
        normalized = line.strip().lower()
        if normalized.startswith("data"):
            return "data_step"
        if normalized.startswith("proc sql"):
            return "proc_sql"
        if normalized.startswith("proc"):
            return normalized.split(";")[0].replace(" ", "_")
        if normalized.startswith("%macro"):
            return "macro"
        return "sas_block"
