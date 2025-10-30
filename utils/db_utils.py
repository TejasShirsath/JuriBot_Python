"""
Database Utilities for JuriBot
Handles local SQLite database operations for logs and saved results
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import hashlib


class JuriBotDB:
    """SQLite database manager for JuriBot"""

    def __init__(self, db_path: str = "juribot.db"):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Documents table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_hash TEXT UNIQUE,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_type TEXT,
                text_length INTEGER,
                language TEXT,
                analysis_summary TEXT,
                metadata TEXT
            )
        """
        )

        # Chat history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata TEXT
            )
        """
        )

        # Analysis results table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                analysis_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result_text TEXT,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        """
        )

        # User queries table (for case law searches)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                query_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                results TEXT,
                metadata TEXT
            )
        """
        )

        # Cost estimations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cost_estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_type TEXT,
                location TEXT,
                complexity TEXT,
                estimated_cost TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def add_document(
        self,
        filename: str,
        file_content: bytes,
        file_type: str,
        text_length: int,
        language: str = "English",
        analysis_summary: str = "",
        metadata: Dict = None,
    ) -> int:
        """
        Add a document record

        Args:
            filename: Original filename
            file_content: Raw file bytes (for hashing)
            file_type: File extension/type
            text_length: Length of extracted text
            language: Detected language
            analysis_summary: Brief summary
            metadata: Additional metadata dict

        Returns:
            Document ID
        """
        # Create hash of file content
        file_hash = hashlib.sha256(file_content).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO documents 
                (filename, file_hash, file_type, text_length, language, 
                 analysis_summary, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    filename,
                    file_hash,
                    file_type,
                    text_length,
                    language,
                    analysis_summary,
                    json.dumps(metadata or {}),
                ),
            )
            doc_id = cursor.lastrowid
            conn.commit()
            return doc_id
        except sqlite3.IntegrityError:
            # Document already exists
            cursor.execute("SELECT id FROM documents WHERE file_hash = ?", (file_hash,))
            doc_id = cursor.fetchone()[0]
            return doc_id
        finally:
            conn.close()

    def add_chat_message(
        self, session_id: str, role: str, message: str, metadata: Dict = None
    ):
        """
        Add a chat message to history

        Args:
            session_id: Unique session identifier
            role: 'user' or 'assistant'
            message: Message content
            metadata: Additional metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO chat_history (session_id, role, message, metadata)
            VALUES (?, ?, ?, ?)
        """,
            (session_id, role, message, json.dumps(metadata or {})),
        )

        conn.commit()
        conn.close()

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """
        Retrieve chat history for a session

        Args:
            session_id: Session identifier
            limit: Maximum number of messages

        Returns:
            List of message dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, role, message, metadata
            FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (session_id, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        messages = []
        for row in rows:
            messages.append(
                {
                    "timestamp": row[0],
                    "role": row[1],
                    "message": row[2],
                    "metadata": json.loads(row[3]) if row[3] else {},
                }
            )

        return list(reversed(messages))

    def add_analysis_result(
        self,
        document_id: Optional[int],
        analysis_type: str,
        result_text: str,
        metadata: Dict = None,
    ) -> int:
        """
        Store analysis result

        Args:
            document_id: Associated document ID (optional)
            analysis_type: Type of analysis performed
            result_text: Analysis output
            metadata: Additional metadata

        Returns:
            Result ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO analysis_results 
            (document_id, analysis_type, result_text, metadata)
            VALUES (?, ?, ?, ?)
        """,
            (document_id, analysis_type, result_text, json.dumps(metadata or {})),
        )

        result_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return result_id

    def add_user_query(
        self, query_text: str, query_type: str, results: str, metadata: Dict = None
    ):
        """
        Log user query (e.g., case law search)

        Args:
            query_text: Search query
            query_type: Type of query
            results: Query results
            metadata: Additional metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_queries 
            (query_text, query_type, results, metadata)
            VALUES (?, ?, ?, ?)
        """,
            (query_text, query_type, results, json.dumps(metadata or {})),
        )

        conn.commit()
        conn.close()

    def add_cost_estimate(
        self,
        case_type: str,
        location: str,
        complexity: str,
        estimated_cost: str,
        details: str,
    ):
        """
        Store cost estimation

        Args:
            case_type: Type of case
            location: Location/jurisdiction
            complexity: Complexity level
            estimated_cost: Estimated cost range
            details: Additional details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO cost_estimates 
            (case_type, location, complexity, estimated_cost, details)
            VALUES (?, ?, ?, ?, ?)
        """,
            (case_type, location, complexity, estimated_cost, details),
        )

        conn.commit()
        conn.close()

    def get_recent_documents(self, limit: int = 10) -> List[Dict]:
        """
        Get recently uploaded documents

        Args:
            limit: Maximum number to return

        Returns:
            List of document records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, filename, uploaded_at, file_type, language
            FROM documents
            ORDER BY uploaded_at DESC
            LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        documents = []
        for row in rows:
            documents.append(
                {
                    "id": row[0],
                    "filename": row[1],
                    "uploaded_at": row[2],
                    "file_type": row[3],
                    "language": row[4],
                }
            )

        return documents

    def get_statistics(self) -> Dict:
        """
        Get usage statistics

        Returns:
            Dictionary with various statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total documents
        cursor.execute("SELECT COUNT(*) FROM documents")
        stats["total_documents"] = cursor.fetchone()[0]

        # Total chat messages
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        stats["total_messages"] = cursor.fetchone()[0]

        # Total queries
        cursor.execute("SELECT COUNT(*) FROM user_queries")
        stats["total_queries"] = cursor.fetchone()[0]

        # Total cost estimates
        cursor.execute("SELECT COUNT(*) FROM cost_estimates")
        stats["total_estimates"] = cursor.fetchone()[0]

        conn.close()
        return stats


def get_db() -> JuriBotDB:
    """
    Get or create database instance

    Returns:
        JuriBotDB instance
    """
    return JuriBotDB()
