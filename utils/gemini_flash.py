"""
Google Gemini 2.0 Flash Integration for JuriBot
Handles all AI reasoning, summarization, and advisory functions
"""

import google.generativeai as genai
import streamlit as st
from typing import Dict, List, Optional
import time


class GeminiFlash:
    """Wrapper class for Google Gemini 2.0 Flash API"""

    def __init__(self, api_key: str):
        """
        Initialize Gemini Flash client

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        self.chat = None

    def analyze_legal_document(
        self, document_text: str, language: str = "English"
    ) -> str:
        """
        Analyze legal document and provide structured output

        Args:
            document_text: The document text to analyze
            language: Language of the document

        Returns:
            Structured analysis from Gemini
        """
        prompt = f"""You are JuriBot, an AI legal advisor for Indian law.
Analyze this legal document and provide structured output in the following format:

## 📋 KEY CLAUSES
List and describe the main legal clauses with their purpose.

## ⚖️ COMPLIANCE ANALYSIS
Identify any compliance issues, missing terms, or legal concerns.

## 📝 SUMMARY
Provide a clear, plain English summary of the document (3-5 sentences).

## 🏛️ RELEVANT LEGAL REFERENCES
List applicable Indian Acts, sections, or notable case law that may be relevant.

## 💼 ADVISORY NOTE
Provide practical advisory points (informational only, not formal legal advice).

Document Language: {language}
Document Text:
{document_text}

Provide detailed, actionable insights specific to Indian legal context."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error during analysis: {str(e)}"

    def chat_message(self, user_message: str, context: Optional[str] = None) -> str:
        """
        Send a chat message with optional context

        Args:
            user_message: User's question or message
            context: Optional context from previous conversation

        Returns:
            AI response
        """
        if context:
            full_message = f"Context: {context}\n\nUser question: {user_message}"
        else:
            full_message = user_message

        prompt = f"""You are JuriBot, an AI legal advisor for Indian law.
Provide clear, helpful responses to legal queries. Always remind users that this is informational only.

{full_message}"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def start_chat(self, initial_message: Optional[str] = None):
        """
        Start a persistent chat session

        Args:
            initial_message: Optional initial system message
        """
        history = []
        if initial_message:
            history.append({"role": "user", "parts": [initial_message]})
            history.append(
                {
                    "role": "model",
                    "parts": [
                        "I understand. I am JuriBot, an AI legal advisor for Indian law. I'll provide informational guidance while reminding users to consult qualified professionals."
                    ],
                }
            )

        self.chat = self.model.start_chat(history=history)

    def send_chat_message(self, message: str) -> str:
        """
        Send message in persistent chat session

        Args:
            message: User message

        Returns:
            AI response
        """
        if self.chat is None:
            self.start_chat()

        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def summarize_conversation(self, conversation_history: List[Dict]) -> str:
        """
        Summarize a conversation history

        Args:
            conversation_history: List of message dictionaries

        Returns:
            Summary text
        """
        conv_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in conversation_history]
        )

        prompt = f"""Summarize the following legal conversation between a user and JuriBot.
Highlight key questions, main legal topics discussed, and important advice given.

Conversation:
{conv_text}

Provide a concise summary in bullet points."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error during summarization: {str(e)}"

    def simulate_case_search(self, query: str) -> str:
        """
        Simulate case law search and provide results

        Args:
            query: Search query for case law

        Returns:
            Simulated case law results
        """
        prompt = f"""You are JuriBot's case law simulation engine.
Based on the following query, simulate 3-5 relevant Indian legal cases.

For each case, provide:
- Case Title (Party A vs Party B)
- Year
- Court
- Relevant Act/Section
- Key Finding (2-3 sentences)
- Why it's relevant to the query

Format the output as a structured list that's easy to parse.

Query: {query}

Note: Indicate that these are simulated/representative results for demonstration purposes."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error during case search: {str(e)}"

    def estimate_legal_costs(
        self, case_type: str, location: str, complexity: str, details: str = ""
    ) -> str:
        """
        Provide AI-enhanced legal cost estimation

        Args:
            case_type: Type of case (civil/criminal/corporate)
            location: Location/jurisdiction
            complexity: Complexity level (low/medium/high)
            details: Additional case details

        Returns:
            Cost estimation with reasoning
        """
        prompt = f"""You are JuriBot's legal cost estimation advisor.
Provide a realistic cost estimation for legal services in India.

Case Details:
- Type: {case_type}
- Location: {location}
- Complexity: {complexity}
- Additional Details: {details}

Provide:
1. Estimated Cost Range (in INR)
2. Cost Breakdown (lawyer fees, court fees, documentation, etc.)
3. Factors Affecting Cost
4. Tips to Optimize Costs
5. Typical Timeline

Format as structured sections. Base estimates on typical Indian legal market rates."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error during cost estimation: {str(e)}"

    def translate_text(self, text: str, target_language: str = "Hindi") -> str:
        """
        Translate text to target language

        Args:
            text: Text to translate
            target_language: Target language (default Hindi)

        Returns:
            Translated text
        """
        prompt = f"""Translate the following text to {target_language}.
Maintain legal terminology accuracy.

Text:
{text}"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error during translation: {str(e)}"

    def detect_and_translate(self, text: str) -> Dict[str, str]:
        """
        Detect language and translate to English if needed

        Args:
            text: Input text

        Returns:
            Dictionary with detected language and translated text
        """
        prompt = f"""Detect the language of this text and translate it to English if it's not already in English.

Text:
{text}

Provide response in this format:
Language: [detected language]
Translation: [English translation or "Already in English"]"""

        try:
            response = self.model.generate_content(prompt)
            return {"result": response.text}
        except Exception as e:
            return {"error": str(e)}


def get_gemini_client() -> Optional[GeminiFlash]:
    """
    Get configured Gemini Flash client from Streamlit secrets

    Returns:
        GeminiFlash instance or None if not configured
    """
    try:
        api_key = st.secrets["secrets"]["GEMINI_API_KEY"]
        if api_key == "YOUR_GEMINI_2_0_FLASH_API_KEY_HERE":
            st.error(
                "⚠️ Please configure your Gemini API key in .streamlit/secrets.toml"
            )
            return None
        return GeminiFlash(api_key)
    except Exception as e:
        st.error(f"Error loading Gemini API key: {str(e)}")
        return None
