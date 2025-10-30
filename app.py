"""
JuriBot: AI-Powered Legal Document Analysis and Advisory System
"""

import streamlit as st

st.set_page_config(
    page_title="JuriBot - AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* Dark mode theme */
    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }
    
    .main-header {
        text-align: center;
        padding: 3rem 0 2rem 0;
    }
    .main-header h1 {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
        color: #ffffff;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .main-header p {
        font-size: 1.3rem;
        color: #b8c6db;
        font-weight: 300;
    }
    
    .feature-box {
        padding: 2rem;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1.2rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    .feature-box:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    .feature-box h3 {
        margin-top: 0;
        color: #64b5f6;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .feature-box p {
        color: #e0e0e0;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
    }
    
    .disclaimer {
        background: rgba(255, 193, 7, 0.15);
        border-left: 4px solid #ffc107;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 3rem 0 1rem 0;
        font-size: 0.95rem;
        color: #ffd54f;
        backdrop-filter: blur(10px);
    }
    .disclaimer strong {
        color: #ffeb3b;
    }
    
    /* Override Streamlit defaults */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    hr {
        border-color: rgba(255, 255, 255, 0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    st.markdown(
        '<div class="main-header"><h1>⚖️ JuriBot</h1><p>AI-Powered Legal Document Analysis for Indian Law</p></div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div class="feature-box">
            <h3>📄 Document Analyzer</h3>
            <p>Upload and analyze legal documents with AI-powered insights</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="feature-box">
            <h3>💬 Legal Chatbot</h3>
            <p>Ask questions about Indian law and get instant answers</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="feature-box">
            <h3>🔍 Case Law Finder</h3>
            <p>Search and explore relevant case law with AI assistance</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="feature-box">
            <h3>💰 Cost Estimator</h3>
            <p>Estimate legal costs based on case type and complexity</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
    <div class="disclaimer">
        <strong>⚠️ Disclaimer:</strong> This system provides informational insights only and does not constitute legal advice. 
        Always consult a qualified legal professional for actual legal matters.
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
