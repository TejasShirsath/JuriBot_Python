"""
JuriBot Utilities Package
Contains all utility modules for document processing, NLP, AI integration, and database operations
"""

__version__ = "1.0.0"
__author__ = "JuriBot Development Team"

# Import main utilities for easy access
from .gemini_flash import GeminiFlash, get_gemini_client
from .db_utils import JuriBotDB, get_db

__all__ = ["GeminiFlash", "get_gemini_client", "JuriBotDB", "get_db"]
