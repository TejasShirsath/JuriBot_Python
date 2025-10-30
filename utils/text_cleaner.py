"""
Text Cleaning Utilities for JuriBot
Handles preprocessing and cleaning of extracted text
"""

import re
import string
from typing import List


def clean_ocr_text(text: str) -> str:
    """
    Clean OCR-extracted text by removing common artifacts

    Args:
        text: Raw OCR text

    Returns:
        Cleaned text
    """
    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Remove multiple newlines (keep max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Fix common OCR errors
    replacements = {
        r"\|": "I",  # Pipe to I
        r"０": "0",  # Full-width zero
        r"[" "`]": "'",  # Normalize quotes
        r'["""]': '"',  # Normalize double quotes
        r"—": "-",  # Em dash to hyphen
        r"–": "-",  # En dash to hyphen
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def remove_headers_footers(text: str) -> str:
    """
    Attempt to remove repeated headers and footers

    Args:
        text: Input text

    Returns:
        Text with headers/footers removed
    """
    lines = text.split("\n")

    # Find lines that appear multiple times (likely headers/footers)
    line_counts = {}
    for line in lines:
        clean_line = line.strip()
        if len(clean_line) > 5 and len(clean_line) < 100:
            line_counts[clean_line] = line_counts.get(clean_line, 0) + 1

    # Remove lines that appear more than 3 times
    repeated_lines = {line for line, count in line_counts.items() if count > 3}

    filtered_lines = [line for line in lines if line.strip() not in repeated_lines]

    return "\n".join(filtered_lines)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text

    Args:
        text: Input text

    Returns:
        Text with normalized whitespace
    """
    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,\.;:!?])", r"\1", text)

    # Add space after punctuation if missing
    text = re.sub(r"([,\.;:!?])([A-Za-z])", r"\1 \2", text)

    return text


def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
    """
    Remove special characters from text

    Args:
        text: Input text
        keep_punctuation: Whether to keep basic punctuation

    Returns:
        Cleaned text
    """
    if keep_punctuation:
        # Keep letters, numbers, spaces, and basic punctuation
        text = re.sub(r"[^a-zA-Z0-9\s\.,;:!?()\-\'\"]+", "", text)
    else:
        # Keep only letters, numbers, and spaces
        text = re.sub(r"[^a-zA-Z0-9\s]+", "", text)

    return text


def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs

    Args:
        text: Input text

    Returns:
        List of paragraphs
    """
    # Split on double newlines or more
    paragraphs = re.split(r"\n\n+", text)

    # Filter out empty paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    return paragraphs


def extract_text_between_markers(
    text: str, start_marker: str, end_marker: str
) -> List[str]:
    """
    Extract text between specific markers

    Args:
        text: Input text
        start_marker: Starting marker pattern
        end_marker: Ending marker pattern

    Returns:
        List of extracted text segments
    """
    pattern = f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    return [match.strip() for match in matches]


def remove_page_numbers(text: str) -> str:
    """
    Remove page numbers from text

    Args:
        text: Input text

    Returns:
        Text with page numbers removed
    """
    # Remove standalone numbers on lines (likely page numbers)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # Remove "Page X" patterns
    text = re.sub(r"Page\s+\d+", "", text, flags=re.IGNORECASE)

    return text


def standardize_legal_terms(text: str) -> str:
    """
    Standardize common legal terms and abbreviations

    Args:
        text: Input text

    Returns:
        Text with standardized terms
    """
    # Common abbreviations to expand
    abbreviations = {
        r"\bvs\.?\b": "versus",
        r"\bV/s\b": "versus",
        r"\bsec\.?\b": "section",
        r"\bart\.?\b": "article",
        r"\bpara\.?\b": "paragraph",
        r"\bcl\.?\b": "clause",
        r"\bHon\'?ble\b": "Honorable",
        r"\bIPC\b": "Indian Penal Code",
        r"\bCrPC\b": "Code of Criminal Procedure",
        r"\bCPC\b": "Code of Civil Procedure",
    }

    for pattern, replacement in abbreviations.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def clean_legal_document(text: str) -> str:
    """
    Apply comprehensive cleaning pipeline for legal documents

    Args:
        text: Raw legal document text

    Returns:
        Cleaned and standardized text
    """
    # Apply cleaning steps in sequence
    text = clean_ocr_text(text)
    text = remove_page_numbers(text)
    text = remove_headers_footers(text)
    text = normalize_whitespace(text)
    text = standardize_legal_terms(text)

    return text


def truncate_text(text: str, max_length: int = 5000, add_ellipsis: bool = True) -> str:
    """
    Truncate text to maximum length

    Args:
        text: Input text
        max_length: Maximum character length
        add_ellipsis: Whether to add ... at the end

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]

    # Try to break at last sentence
    last_period = truncated.rfind(".")
    if last_period > max_length * 0.8:  # If period is in last 20%
        truncated = truncated[: last_period + 1]

    if add_ellipsis:
        truncated += "..."

    return truncated
