"""Unit tests for code chunker"""

import pytest

from src.data.corpus_loader import CodeChunker
from tests.fixtures.sample_sas_code import SAMPLE_SAS_CODE


def test_chunk_code_basic():
    """Test basic code chunking"""
    chunker = CodeChunker(chunk_size=50, overlap=10)
    chunks = chunker.chunk_code(SAMPLE_SAS_CODE, "test_code")

    assert len(chunks) > 0
    assert all("id" in chunk for chunk in chunks)
    assert all("text" in chunk for chunk in chunks)


def test_chunk_preserves_code():
    """Test that chunking preserves all code"""
    chunker = CodeChunker(chunk_size=100, overlap=20)
    chunks = chunker.chunk_code(SAMPLE_SAS_CODE, "test_code")

    combined = " ".join([chunk["text"] for chunk in chunks])
    # Check that original code is mostly preserved
    assert "mydata" in combined
    assert "subjid" in combined


def test_chunk_ids_unique():
    """Test that chunk IDs are unique"""
    chunker = CodeChunker()
    chunks = chunker.chunk_code(SAMPLE_SAS_CODE, "test_code")

    ids = [chunk["id"] for chunk in chunks]
    assert len(ids) == len(set(ids)), "Chunk IDs should be unique"
