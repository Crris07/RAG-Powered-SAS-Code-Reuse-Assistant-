"""Deterministic demo provider for offline prototype generation."""

import re

from src.llm.llm_adapter import LLMProvider


class DemoProvider(LLMProvider):
    """Generate a transparent SAS adaptation without external LLM calls."""

    SAS_BLOCK_RE = re.compile(r"```sas\s*(.*?)```", re.IGNORECASE | re.DOTALL)

    def is_available(self) -> bool:
        """Demo generation is always available."""
        return True

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Return a reusable SAS suggestion based on the top retrieved example."""
        requirement = self._extract_requirement(user_prompt)
        source_code = self._extract_source_code(user_prompt, requirement)
        adapted_code = self._adapt_code(source_code, requirement)

        return (
            "/*\n"
            "Prototype SAS suggestion generated from retrieved historical code.\n"
            f"Requirement: {requirement}\n"
            "Assumptions:\n"
            "- Source SDTM/ADaM libraries are available as SDTM and ADAM.\n"
            "- Study-specific formats, population flags, and derivation rules should be reviewed.\n"
            "- Output dataset names may need to be aligned with the target study standard.\n"
            "*/\n\n"
            f"{adapted_code}\n\n"
            "/* Review checklist:\n"
            "1. Confirm input dataset names and key variables.\n"
            "2. Confirm population flag derivations against the SAP/specification.\n"
            "3. Run SAS syntax validation before production use.\n"
            "*/"
        )

    def _extract_requirement(self, prompt: str) -> str:
        marker = "Adapt this code to meet the new requirement:"
        if marker not in prompt:
            return prompt.strip().splitlines()[-1]
        return prompt.split(marker, 1)[1].split("Provide:", 1)[0].strip()

    def _extract_source_code(self, prompt: str, requirement: str) -> str:
        matches = [match.strip() for match in self.SAS_BLOCK_RE.findall(prompt)]
        requested_dataset = self._infer_output_dataset(requirement.lower()).split(".")[-1]
        dataset_pattern = re.compile(
            rf"^\s*data\s+(?:[A-Za-z0-9_]+\.)?{re.escape(requested_dataset)}\b",
            re.IGNORECASE | re.MULTILINE,
        )

        for match in matches:
            if dataset_pattern.search(match):
                return match

        for match in matches:
            if re.search(r"^\s*data\s+", match, re.IGNORECASE | re.MULTILINE):
                return match
        if matches:
            return matches[0]
        return (
            "data work.analysis_dataset;\n"
            "    set adam.adsl;\n"
            "run;"
        )

    def _adapt_code(self, code: str, requirement: str) -> str:
        lowered = requirement.lower()
        output_name = self._infer_output_dataset(lowered)
        adapted = code

        adapted = re.sub(r"\bdata\s+([A-Za-z0-9_.]+)", f"data {output_name}", adapted, count=1, flags=re.IGNORECASE)
        adapted = adapted.replace("work.adsl", output_name)

        if "safety" in lowered and "saffl" not in adapted.lower():
            safety_logic = (
                "\n  /* Safety population flag placeholder - verify against study rules. */\n"
                "  if not missing(trtsdt) then saffl = 'Y';\n"
                "  else saffl = 'N';"
            )
            adapted = self._insert_before_run(adapted, safety_logic)

        if "tlf" in lowered or "table" in lowered or "listing" in lowered:
            adapted += (
                "\n\nproc report data="
                f"{output_name} nowd;\n"
                "    columns _all_;\n"
                "run;"
            )

        return adapted

    def _insert_before_run(self, code: str, inserted_code: str) -> str:
        match = re.search(r"^\s*run\s*;", code, re.IGNORECASE | re.MULTILINE)
        if not match:
            return f"{code.rstrip()}\n{inserted_code}"
        return f"{code[:match.start()].rstrip()}\n{inserted_code}\n{code[match.start():].lstrip()}"

    def _infer_output_dataset(self, requirement: str) -> str:
        dataset_map = {
            "adsl": "adam.adsl",
            "adae": "adam.adae",
            "adlb": "adam.adlb",
            "advs": "adam.advs",
            "adtte": "adam.adtte",
        }
        for keyword, dataset in dataset_map.items():
            if keyword in requirement:
                return dataset
        if "listing" in requirement:
            return "work.generated_listing"
        if "table" in requirement or "tlf" in requirement:
            return "work.generated_tlf"
        return "work.generated_adam"
