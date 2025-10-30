"""
NLP Utilities for JuriBot
Handles local text processing, entity recognition, and clause detection
"""

import re
import nltk
import spacy
from typing import List, Dict, Tuple
import string

# Download required NLTK data (run once)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None


def tokenize_sentences(text: str) -> List[str]:
    """
    Split text into sentences using NLTK

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    from nltk.tokenize import sent_tokenize

    return sent_tokenize(text)


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities using spaCy

    Args:
        text: Input text

    Returns:
        Dictionary of entity types and their values
    """
    if nlp is None:
        return {"error": "spaCy model not loaded"}

    doc = nlp(text)
    entities = {
        "PERSON": [],
        "ORG": [],
        "DATE": [],
        "GPE": [],  # Geopolitical entities (locations)
        "LAW": [],
        "MONEY": [],
        "CARDINAL": [],
        "OTHER": [],
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
        else:
            entities["OTHER"].append(f"{ent.text} ({ent.label_})")

    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))

    return entities


def detect_legal_clauses(text: str) -> List[Dict[str, str]]:
    """
    Detect common legal clauses and patterns

    Args:
        text: Input legal document text

    Returns:
        List of detected clauses with type and content
    """
    clauses = []

    # Common legal clause patterns for Indian legal documents
    patterns = {
        "WHEREAS": r"WHEREAS\s+[^;]+;?",
        "PROVIDED": r"PROVIDED\s+(?:THAT|that)\s+[^;.]+[;.]?",
        "NOTWITHSTANDING": r"NOTWITHSTANDING\s+[^;.]+[;.]?",
        "SUBJECT TO": r"SUBJECT\s+TO\s+[^;.]+[;.]?",
        "IN WITNESS WHEREOF": r"IN\s+WITNESS\s+WHEREOF[^.]+\.",
        "THEREFORE": r"THEREFORE[^;.]+[;.]?",
        "AGREEMENT": r"(?:THIS\s+)?AGREEMENT\s+[^;.]+[;.]?",
        "PARTIES": r"(?:THE\s+)?PARTIES?\s+(?:HERETO|TO\s+THIS)[^;.]+[;.]?",
        "CONSIDERATION": r"CONSIDERATION\s+[^;.]+[;.]?",
        "INDEMNITY": r"INDEMNIT(?:Y|IES)\s+[^;.]+[;.]?",
        "TERMINATION": r"TERMINATION\s+[^;.]+[;.]?",
        "JURISDICTION": r"JURISDICTION\s+[^;.]+[;.]?",
        "FORCE MAJEURE": r"FORCE\s+MAJEURE\s+[^;.]+[;.]?",
    }

    for clause_type, pattern in patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            clauses.append(
                {
                    "type": clause_type,
                    "content": match.group(0).strip(),
                    "position": match.start(),
                }
            )

    # Sort by position in document
    clauses.sort(key=lambda x: x["position"])

    return clauses


def detect_indian_acts(text: str) -> List[str]:
    """
    Detect references to Indian Acts and legal provisions

    Args:
        text: Input text

    Returns:
        List of detected Act references
    """
    acts = []

    # Common Indian Acts patterns
    act_patterns = [
        r"Indian\s+Penal\s+Code(?:\s*,?\s*\d{4})?",
        r"Code\s+of\s+Criminal\s+Procedure(?:\s*,?\s*\d{4})?",
        r"Code\s+of\s+Civil\s+Procedure(?:\s*,?\s*\d{4})?",
        r"Indian\s+Contract\s+Act(?:\s*,?\s*\d{4})?",
        r"Transfer\s+of\s+Property\s+Act(?:\s*,?\s*\d{4})?",
        r"Companies\s+Act(?:\s*,?\s*\d{4})?",
        r"Income\s+Tax\s+Act(?:\s*,?\s*\d{4})?",
        r"Goods\s+and\s+Services\s+Tax\s+Act(?:\s*,?\s*\d{4})?",
        r"Consumer\s+Protection\s+Act(?:\s*,?\s*\d{4})?",
        r"Information\s+Technology\s+Act(?:\s*,?\s*\d{4})?",
        r"Negotiable\s+Instruments\s+Act(?:\s*,?\s*\d{4})?",
        r"Arbitration\s+and\s+Conciliation\s+Act(?:\s*,?\s*\d{4})?",
        r"Constitution\s+of\s+India",
        r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Act(?:\s*,?\s*\d{4})?",
    ]

    # Section references
    section_pattern = (
        r"(?:Section|Sec\.|s\.|§)\s*\d+(?:\s*\([a-z0-9]+\))?(?:\s+(?:of|to)\s+[^.;]+)?"
    )

    for pattern in act_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            acts.append(match.group(0).strip())

    # Find section references
    section_matches = re.finditer(section_pattern, text, re.IGNORECASE)
    for match in section_matches:
        acts.append(match.group(0).strip())

    return list(set(acts))


def extract_dates(text: str) -> List[str]:
    """
    Extract dates from text

    Args:
        text: Input text

    Returns:
        List of detected dates
    """
    date_patterns = [
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
        r"\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}",
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}",
    ]

    dates = []
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        dates.extend([match.group(0) for match in matches])

    return list(set(dates))


def extract_key_phrases(text: str, n: int = 10) -> List[Tuple[str, int]]:
    """
    Extract key phrases using basic frequency analysis

    Args:
        text: Input text
        n: Number of top phrases to return

    Returns:
        List of (phrase, frequency) tuples
    """
    from nltk.corpus import stopwords
    from collections import Counter

    # Tokenize
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    filtered_words = [w for w in words if w not in stop_words]

    # Count frequencies
    word_freq = Counter(filtered_words)

    return word_freq.most_common(n)


def analyze_document_structure(text: str) -> Dict:
    """
    Analyze overall document structure

    Args:
        text: Input document text

    Returns:
        Dictionary with structure analysis
    """
    sentences = tokenize_sentences(text)
    words = text.split()

    return {
        "total_characters": len(text),
        "total_words": len(words),
        "total_sentences": len(sentences),
        "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
        "has_sections": bool(
            re.search(r"(?:SECTION|Section|Article|ARTICLE)\s+\d+", text)
        ),
        "has_numbering": bool(re.search(r"^\s*\d+[\.\)]\s+", text, re.MULTILINE)),
        "has_legal_formatting": bool(
            re.search(r"WHEREAS|PROVIDED|NOTWITHSTANDING", text, re.IGNORECASE)
        ),
    }
