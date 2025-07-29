"""
Tests for text utilities.
"""

import pytest
from textregress.utils.text import chunk_text, pad_chunks


def test_chunk_text_empty():
    """Test chunking empty text."""
    assert chunk_text("", max_length=10) == []


def test_chunk_text_no_overlap():
    """Test chunking text without overlap."""
    text = "This is a test sentence that needs to be chunked."
    chunks = chunk_text(text, max_length=10)
    assert len(chunks) == 5
    assert all(len(chunk) <= 10 for chunk in chunks)
    assert "".join(chunks) == text


def test_chunk_text_with_overlap():
    """Test chunking text with overlap."""
    text = "This is a test sentence that needs to be chunked."
    chunks = chunk_text(text, max_length=10, overlap=2)
    assert len(chunks) == 5
    assert all(len(chunk) <= 10 for chunk in chunks)
    # Verify overlap
    for i in range(len(chunks) - 1):
        assert chunks[i][-2:] == chunks[i + 1][:2]


def test_pad_chunks():
    """Test padding chunks to maximum length."""
    chunks = ["short", "medium length", "very long text here"]
    max_length = 15
    padded = pad_chunks(chunks, max_length)
    assert len(padded) == len(chunks)
    assert all(len(chunk) == max_length for chunk in padded)
    assert padded[0].startswith("short")
    assert padded[1].startswith("medium length")
    assert padded[2].startswith("very long text here") 