"""
Legal Chatbot Page
Interactive Q&A system with context-aware responses
"""

import streamlit as st
import uuid
from datetime import datetime
import pandas as pd

from utils.gemini_flash import get_gemini_client
from utils.db_utils import get_db

st.set_page_config(page_title="Legal Chatbot - JuriBot", page_icon="💬", layout="wide")

# Initialize
db = get_db()
gemini = get_gemini_client()

st.title("💬 Legal Chatbot")
st.markdown("Ask questions about Indian law and get AI-powered responses")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "gemini_chat" not in st.session_state and gemini:
    # Initialize Gemini chat with system message
    gemini.start_chat(
        "You are JuriBot, an AI legal advisor for Indian law. "
        "Provide clear, helpful responses. Always remind users this is informational only."
    )
    st.session_state.gemini_chat = True

# Sidebar
with st.sidebar:
    st.header("💬 Chat Options")

    # Chat controls
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        if gemini:
            gemini.start_chat(
                "You are JuriBot, an AI legal advisor for Indian law. "
                "Provide clear, helpful responses. Always remind users this is informational only."
            )
        st.rerun()

    st.markdown("---")

    # Suggested topics
    st.subheader("💡 Suggested Topics")

    topics = [
        "Indian Contract Act provisions",
        "Property transfer laws",
        "Consumer protection rights",
        "Employment law basics",
        "Intellectual property rights",
        "Criminal procedure overview",
        "Tax compliance requirements",
        "Corporate governance",
    ]

    for topic in topics:
        if st.button(topic, key=f"topic_{topic}"):
            st.session_state.pending_question = f"Tell me about {topic}"

    st.markdown("---")

    # Chat statistics
    st.subheader("📊 Session Stats")
    st.metric("Messages", len(st.session_state.chat_history))

    # Export chat
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("📥 Export Chat")

        if st.button("💾 Download Chat History"):
            chat_export = "JuriBot Chat History\n"
            chat_export += "=" * 50 + "\n\n"

            for msg in st.session_state.chat_history:
                role = "You" if msg["role"] == "user" else "JuriBot"
                chat_export += f"{role} [{msg['timestamp']}]:\n{msg['content']}\n\n"

            chat_export += "=" * 50 + "\n"
            chat_export += "Disclaimer: This is informational only, not legal advice.\n"

            st.download_button(
                label="📥 Download as TXT",
                data=chat_export,
                file_name=f"juribot_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
            )

# Main chat interface
if gemini is None:
    st.error(
        "⚠️ Gemini API not configured. Please add your API key to .streamlit/secrets.toml"
    )
else:

    # Display chat history
    chat_container = st.container()

    with chat_container:
        if not st.session_state.chat_history:
            st.info(
                """
            👋 **Welcome to JuriBot Legal Assistant!**
            
            I can help you with:
            - Understanding Indian legal concepts
            - Explaining Acts and provisions
            - General legal guidance (informational only)
            - Legal terminology and definitions
            
            Ask me anything about Indian law!
            """
            )
        else:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    st.caption(message["timestamp"])

    # Chat input
    user_input = st.chat_input("Ask a legal question...")

    # Handle pending question from sidebar
    if "pending_question" in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question

    if user_input:
        # Add user message to history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_message = {"role": "user", "content": user_input, "timestamp": timestamp}

        st.session_state.chat_history.append(user_message)

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
            st.caption(timestamp)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                # Send to Gemini
                response = gemini.send_chat_message(user_input)

                # Display response
                st.markdown(response)
                st.caption(timestamp)

                # Add to history
                assistant_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": timestamp,
                }

                st.session_state.chat_history.append(assistant_message)

                # Save to database
                db.add_chat_message(
                    session_id=st.session_state.session_id,
                    role="user",
                    message=user_input,
                )

                db.add_chat_message(
                    session_id=st.session_state.session_id,
                    role="assistant",
                    message=response,
                )

        st.rerun()

    # Summarize conversation feature
    if len(st.session_state.chat_history) > 4:
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button("📋 Summarize Conversation", use_container_width=True):
                with st.spinner("Generating summary..."):

                    # Prepare conversation for summary
                    conv_history = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.chat_history
                    ]

                    summary = gemini.summarize_conversation(conv_history)

                    st.subheader("📋 Conversation Summary")
                    st.markdown(summary)

                    # Option to download summary
                    summary_text = f"""JuriBot Conversation Summary
{'='*50}

Session ID: {st.session_state.session_id}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

SUMMARY:
{summary}

{'='*50}
Full chat history available in chat export.
"""

                    st.download_button(
                        label="📥 Download Summary",
                        data=summary_text,
                        file_name=f"chat_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain",
                    )

# Quick help section
with st.expander("❓ How to use the chatbot"):
    st.markdown(
        """
    **Tips for better responses:**
    
    1. **Be specific**: Instead of "Tell me about contracts", try "What are the essential elements of a valid contract under Indian Contract Act?"
    
    2. **Provide context**: Mention relevant details like jurisdiction, type of case, or specific Acts
    
    3. **Follow-up questions**: The chatbot maintains context, so you can ask follow-up questions
    
    4. **Use suggested topics**: Click the sidebar buttons for common legal topics
    
    5. **Export your chat**: Save the conversation for future reference
    
    **Example questions:**
    - "What is Section 420 of the Indian Penal Code?"
    - "Explain the concept of consideration in contracts"
    - "What are the rights of a tenant in Maharashtra?"
    - "How does the Consumer Protection Act protect buyers?"
    """
    )

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666; font-size: 0.85em;">
⚠️ This chatbot provides informational guidance only and does not constitute legal advice.<br>
Always consult a qualified legal professional for actual legal matters.
</div>
""",
    unsafe_allow_html=True,
)
