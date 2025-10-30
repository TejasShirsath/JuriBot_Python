"""
Document Analyzer Page
Handles document upload, OCR processing, and AI-powered legal analysis
"""

import streamlit as st
import PyPDF2
from docx import Document
from PIL import Image
import io
from langdetect import detect
import pandas as pd

from utils.ocr_utils import (
    extract_text_from_image,
    extract_text_from_pdf_ocr,
    is_scanned_pdf,
)
from utils.nlp_utils import (
    extract_named_entities,
    detect_legal_clauses,
    detect_indian_acts,
    extract_dates,
    analyze_document_structure,
)
from utils.text_cleaner import clean_legal_document, truncate_text
from utils.gemini_flash import get_gemini_client
from utils.db_utils import get_db

st.set_page_config(
    page_title="Document Analyzer - JuriBot", page_icon="📄", layout="wide"
)

# Initialize
db = get_db()
gemini = get_gemini_client()

st.title("📄 Document Analyzer")
st.markdown("Upload and analyze legal documents with AI-powered insights")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    file_type = st.radio("Upload Type", ["📁 File Upload", "✍️ Text Input"])

    if file_type == "📁 File Upload":
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx", "jpg", "jpeg", "png"],
            help="Supported formats: PDF, DOCX, JPG, PNG",
        )
    else:
        uploaded_file = None

    st.markdown("---")

    # Language options
    auto_translate = st.checkbox("Auto-translate Hindi to English", value=True)

    st.markdown("---")

    # Export options
    st.subheader("📥 Export")
    export_format = st.selectbox("Format", ["TXT", "PDF"])


def extract_text_from_pdf(pdf_file):
    """Extract text from PDF using PyPDF2"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = []
        for page in pdf_reader.pages:
            text.append(page.extract_text())
        return "\n\n".join(text)
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


def extract_text_from_docx(docx_file):
    """Extract text from DOCX"""
    try:
        doc = Document(docx_file)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n\n".join(text)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def detect_language(text):
    """Detect language of text"""
    try:
        lang = detect(text[:1000])  # Check first 1000 chars
        return "Hindi" if lang == "hi" else "English"
    except:
        return "English"


# Main content
if file_type == "📁 File Upload" and uploaded_file:

    with st.spinner("Processing document..."):

        # Extract text based on file type
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension == "pdf":
            # Try regular extraction first
            pdf_text = extract_text_from_pdf(uploaded_file)

            if is_scanned_pdf(pdf_text):
                st.info("📸 Detected scanned PDF. Running OCR...")
                uploaded_file.seek(0)
                extracted_text = extract_text_from_pdf_ocr(uploaded_file)
            else:
                extracted_text = pdf_text

        elif file_extension == "docx":
            extracted_text = extract_text_from_docx(uploaded_file)

        elif file_extension in ["jpg", "jpeg", "png"]:
            st.info("📸 Running OCR on image...")
            image = Image.open(uploaded_file)
            extracted_text = extract_text_from_image(image)

        # Clean text
        cleaned_text = clean_legal_document(extracted_text)

        # Detect language
        detected_lang = detect_language(cleaned_text)

        st.success(f"✅ Document processed! Detected language: {detected_lang}")

    # Display extracted text
    st.subheader("📝 Extracted Text")

    with st.expander("View/Edit Extracted Text", expanded=False):
        edited_text = st.text_area(
            "Text content",
            cleaned_text,
            height=300,
            help="You can edit the extracted text before analysis",
        )

    # Use edited text if modified
    final_text = edited_text if "edited_text" in locals() else cleaned_text

    # Document statistics
    doc_stats = analyze_document_structure(final_text)

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    with stat_col1:
        st.metric("Words", doc_stats["total_words"])
    with stat_col2:
        st.metric("Sentences", doc_stats["total_sentences"])
    with stat_col3:
        st.metric("Characters", doc_stats["total_characters"])
    with stat_col4:
        st.metric("Avg Sentence Length", f"{doc_stats['avg_sentence_length']:.1f}")

    # Translation if needed
    if detected_lang == "Hindi" and auto_translate and gemini:
        with st.spinner("Translating to English..."):
            translation_result = gemini.detect_and_translate(final_text[:3000])
            if "result" in translation_result:
                st.info("🔄 Text translated to English for analysis")
                final_text = translation_result["result"]

    # Local NLP Analysis
    st.subheader("🔍 Local NLP Analysis")

    nlp_col1, nlp_col2 = st.columns(2)

    with nlp_col1:
        with st.expander("👤 Named Entities", expanded=True):
            entities = extract_named_entities(final_text[:5000])
            for entity_type, values in entities.items():
                if values:
                    st.markdown(f"**{entity_type}**: {', '.join(values[:5])}")

    with nlp_col2:
        with st.expander("📜 Legal Clauses", expanded=True):
            clauses = detect_legal_clauses(final_text)
            if clauses:
                for clause in clauses[:5]:
                    st.markdown(f"- **{clause['type']}**: {clause['content'][:100]}...")
            else:
                st.info("No standard legal clauses detected")

    # Indian Acts detection
    with st.expander("🏛️ Detected Legal References"):
        acts = detect_indian_acts(final_text)
        if acts:
            st.markdown("Found references to:")
            for act in acts[:10]:
                st.markdown(f"- {act}")
        else:
            st.info("No specific Act references detected")

    # Dates
    dates = extract_dates(final_text)
    if dates:
        with st.expander("📅 Important Dates"):
            st.markdown(", ".join(dates[:10]))

    # AI Analysis
    st.subheader("🤖 AI-Powered Legal Analysis")

    if gemini is None:
        st.error(
            "⚠️ Gemini API not configured. Please add your API key to .streamlit/secrets.toml"
        )
    else:
        if st.button("🚀 Analyze with Gemini 2.0 Flash", type="primary"):

            with st.spinner("Analyzing document with AI... This may take a moment."):

                # Truncate if too long
                analysis_text = truncate_text(final_text, max_length=15000)

                # Get analysis
                analysis = gemini.analyze_legal_document(analysis_text, detected_lang)

                # Store in database
                if uploaded_file:
                    doc_id = db.add_document(
                        filename=uploaded_file.name,
                        file_content=uploaded_file.getvalue(),
                        file_type=file_extension,
                        text_length=len(final_text),
                        language=detected_lang,
                        analysis_summary=analysis[:500],
                    )
                    db.add_analysis_result(
                        document_id=doc_id,
                        analysis_type="legal_analysis",
                        result_text=analysis,
                    )

                # Display analysis
                st.markdown("---")
                st.markdown(analysis)

                # Save to session state for export
                st.session_state["last_analysis"] = {
                    "filename": uploaded_file.name if uploaded_file else "document",
                    "text": final_text,
                    "analysis": analysis,
                }

                st.success("✅ Analysis complete!")

    # Export functionality
    if "last_analysis" in st.session_state:
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            # Export as TXT
            export_text = f"""JuriBot Analysis Report
{'='*50}

Document: {st.session_state['last_analysis']['filename']}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

EXTRACTED TEXT:
{st.session_state['last_analysis']['text'][:5000]}

{'='*50}

AI ANALYSIS:
{st.session_state['last_analysis']['analysis']}

{'='*50}
Disclaimer: This is an informational analysis only, not legal advice.
"""

            st.download_button(
                label="📥 Download as TXT",
                data=export_text,
                file_name=f"juribot_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
            )

        with col2:
            st.info("💡 PDF export requires additional libraries. Use TXT for now.")

elif file_type == "✍️ Text Input":

    st.subheader("✍️ Enter or Paste Text")

    input_text = st.text_area(
        "Legal document text",
        height=300,
        placeholder="Paste your legal document text here...",
        help="Enter the text you want to analyze",
    )

    if input_text and len(input_text) > 50:

        # Clean text
        cleaned_text = clean_legal_document(input_text)

        # Detect language
        detected_lang = detect_language(cleaned_text)

        st.info(
            f"📝 Text length: {len(cleaned_text)} characters | Language: {detected_lang}"
        )

        # Local NLP
        st.subheader("🔍 Quick Analysis")

        entities = extract_named_entities(cleaned_text[:3000])
        clauses = detect_legal_clauses(cleaned_text)
        acts = detect_indian_acts(cleaned_text)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Entities Found", sum(len(v) for v in entities.values()))
        with col2:
            st.metric("Legal Clauses", len(clauses))
        with col3:
            st.metric("Act References", len(acts))

        # AI Analysis
        if gemini and st.button("🚀 Analyze with AI", type="primary"):

            with st.spinner("Analyzing..."):
                analysis = gemini.analyze_legal_document(cleaned_text, detected_lang)

                st.markdown("---")
                st.markdown(analysis)

                # Save for export
                st.session_state["last_analysis"] = {
                    "filename": "text_input",
                    "text": cleaned_text,
                    "analysis": analysis,
                }

else:
    # Welcome screen
    st.info(
        """
    👈 **Get Started**: Choose an upload method from the sidebar
    
    **Supported Formats:**
    - 📄 PDF documents (native and scanned)
    - 📝 Word documents (.docx)
    - 🖼️ Images (JPG, PNG) with OCR
    - ✍️ Direct text input
    
    **What we analyze:**
    - Key legal clauses and terms
    - Compliance issues and gaps
    - Named entities (people, organizations, dates)
    - References to Indian Acts and sections
    - Plain language summary
    - Advisory insights
    """
    )

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666; font-size: 0.85em;">
⚠️ This analysis is for informational purposes only and does not constitute legal advice.
</div>
""",
    unsafe_allow_html=True,
)
