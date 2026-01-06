# JuriBot

## Overview

AI-powered legal document analysis system for the Indian legal domain. Combines local NLP processing with Google Gemini 2.0 Flash AI for intelligent document analysis, legal chatbot, case law research, and cost estimation.

## Tech Stack

- **Frontend**: Streamlit
- **AI Engine**: OpenRouter (openai/gpt-oss-120b:free)
- **Local NLP**: spaCy, NLTK, Tesseract OCR, pdf2image
- **Database**: SQLite
- **Visualization**: Plotly

## Features

- **Document Analyzer** - Extract and analyze text from PDFs, images, and Word documents
- **Legal Chatbot** - Context-aware Q&A with AI
- **Case Law Finder** - Search and summarize relevant case law
- **Cost Estimator** - Estimate legal costs with visualizations

## Windows Usage

### Setup with Virtual Environment

1. **Create virtual environment:**

   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**

   ```bash
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLP models:**

   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt_tab'); nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
   ```

5. **Install Tesseract OCR:**

   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH or update path in `utils/ocr_utils.py`

6. **Install Poppler:**

   - Download from: https://github.com/oschwartz10612/poppler-windows/releases
   - Add to PATH

7. **Configure API key:**

   - Add your OpenRouter API key to `.streamlit/secrets.toml`:
     ```toml
     [secrets]
     OPENROUTER_API_KEY = "your-openrouter-api-key-here"
     ```

8. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

**Disclaimer:** This system provides informational insights only, not formal legal advice.
