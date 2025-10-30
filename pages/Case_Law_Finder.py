"""
Case Law Finder Page
AI-powered case law search and simulation
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.gemini_flash import get_gemini_client
from utils.db_utils import get_db

st.set_page_config(
    page_title="Case Law Finder - JuriBot", page_icon="🔍", layout="wide"
)

# Initialize
db = get_db()
gemini = get_gemini_client()

st.title("🔍 Case Law Finder")
st.markdown("Search and explore relevant Indian case law with AI assistance")

# Sidebar
with st.sidebar:
    st.header("🔎 Search Filters")

    # Search category
    category = st.selectbox(
        "Legal Domain",
        [
            "All",
            "Constitutional Law",
            "Criminal Law",
            "Civil Law",
            "Corporate Law",
            "Property Law",
            "Family Law",
            "Labor & Employment",
            "Tax Law",
            "Intellectual Property",
            "Consumer Protection",
        ],
    )

    # Court level
    court_level = st.multiselect(
        "Court Level",
        ["Supreme Court", "High Court", "District Court", "Tribunal"],
        default=["Supreme Court", "High Court"],
    )

    # Year range
    st.markdown("**Year Range**")
    col1, col2 = st.columns(2)
    with col1:
        year_from = st.number_input("From", min_value=1950, max_value=2025, value=2000)
    with col2:
        year_to = st.number_input("To", min_value=1950, max_value=2025, value=2025)

    st.markdown("---")

    # Recent searches
    st.subheader("📜 Recent Searches")

    if "recent_searches" not in st.session_state:
        st.session_state.recent_searches = []

    if st.session_state.recent_searches:
        for i, search in enumerate(st.session_state.recent_searches[-5:]):
            if st.button(f"🔍 {search[:30]}...", key=f"recent_{i}"):
                st.session_state.pending_search = search
    else:
        st.info("No recent searches")

# Main content
st.subheader("🔍 Search for Case Law")

# Search examples
with st.expander("💡 Example Searches"):
    st.markdown(
        """
    - "Tenant eviction under Maharashtra Rent Control Act"
    - "Intellectual property infringement cases"
    - "Section 138 NI Act dishonor of cheque"
    - "Right to privacy landmark judgments"
    - "Corporate fraud under Companies Act"
    - "Consumer rights and product liability"
    - "Breach of contract cases"
    - "Defamation and free speech"
    """
    )

# Search input
search_query = st.text_input(
    "Enter your search query",
    placeholder="e.g., property dispute between co-owners",
    help="Describe the legal issue or topic you want to search for",
)

# Handle pending search from sidebar
if "pending_search" in st.session_state:
    search_query = st.session_state.pending_search
    del st.session_state.pending_search

if gemini is None:
    st.error(
        "⚠️ Gemini API not configured. Please add your API key to .streamlit/secrets.toml"
    )
else:

    # Search button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        search_button = st.button(
            "🚀 Search Case Law", type="primary", use_container_width=True
        )

    if search_button and search_query:

        # Add to recent searches
        if search_query not in st.session_state.recent_searches:
            st.session_state.recent_searches.append(search_query)

        with st.spinner("🔍 Searching case law database... This may take a moment."):

            # Enhance query with filters
            enhanced_query = search_query
            if category != "All":
                enhanced_query += f" (Domain: {category})"
            if court_level:
                enhanced_query += f" (Courts: {', '.join(court_level)})"
            enhanced_query += f" (Years: {year_from}-{year_to})"

            # Get AI-simulated results
            results = gemini.simulate_case_search(enhanced_query)

            # Store in database
            db.add_user_query(
                query_text=search_query,
                query_type="case_law_search",
                results=results,
                metadata={
                    "category": category,
                    "court_level": court_level,
                    "year_range": f"{year_from}-{year_to}",
                },
            )

            # Display results
            st.markdown("---")
            st.subheader("📚 Search Results")

            st.info(
                """
            **Note**: These are AI-simulated case references for demonstration purposes. 
            For actual legal work, always verify with official law databases like:
            - Indian Kanoon (indiankanoon.org)
            - Supreme Court of India website
            - SCC Online
            - Manupatra
            """
            )

            # Display the AI response
            st.markdown(results)

            # Parse and structure results (basic parsing)
            st.markdown("---")

            # Quick actions
            col1, col2, col3 = st.columns(3)

            with col1:
                st.download_button(
                    label="📥 Download Results",
                    data=f"""Case Law Search Results
{'='*60}

Query: {search_query}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Filters: {category}, {', '.join(court_level)}, {year_from}-{year_to}

{'='*60}

{results}

{'='*60}
Disclaimer: These are simulated results for demonstration.
Always verify with official legal databases.
""",
                    file_name=f"case_search_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                )

            with col2:
                if st.button("🔄 Refine Search"):
                    st.info("Modify your query above and search again")

            with col3:
                if st.button("💬 Discuss in Chat"):
                    st.session_state.chat_context = f"Case search: {search_query}"
                    st.info("Context saved! Go to Legal Chatbot to discuss.")

# Predefined case categories
st.markdown("---")
st.subheader("📂 Browse by Category")

categories_data = {
    "Constitutional Law": [
        "Fundamental Rights",
        "Judicial Review",
        "Federalism",
        "Emergency Provisions",
    ],
    "Criminal Law": [
        "IPC Offenses",
        "CrPC Procedures",
        "Bail Applications",
        "Evidence Act",
    ],
    "Civil Law": ["Contract Disputes", "Property Rights", "Torts", "Succession"],
    "Corporate Law": ["Companies Act", "Insolvency", "Securities Law", "M&A"],
}

cat_cols = st.columns(4)

for idx, (cat_name, topics) in enumerate(categories_data.items()):
    with cat_cols[idx]:
        st.markdown(f"**{cat_name}**")
        for topic in topics:
            if st.button(topic, key=f"cat_{topic}"):
                st.session_state.pending_search = (
                    f"Notable cases on {topic} in Indian law"
                )
                st.rerun()

# Landmark cases section
st.markdown("---")
st.subheader("⭐ Landmark Cases")

with st.expander("View Notable Indian Supreme Court Cases"):
    st.markdown(
        """
    **Constitutional Law:**
    - Kesavananda Bharati v. State of Kerala (1973) - Basic Structure Doctrine
    - Maneka Gandhi v. Union of India (1978) - Article 21 expansion
    - Minerva Mills v. Union of India (1980) - Parliamentary limitations
    
    **Criminal Law:**
    - State of Maharashtra v. Ramdas Shrinivas (2018) - Section 497 IPC struck down
    - Navtej Singh Johar v. Union of India (2018) - Section 377 partially struck down
    - Shreya Singhal v. Union of India (2015) - Section 66A IT Act struck down
    
    **Civil Rights:**
    - K.S. Puttaswamy v. Union of India (2017) - Right to Privacy
    - Vishaka v. State of Rajasthan (1997) - Sexual harassment guidelines
    - MC Mehta cases - Environmental law precedents
    
    **Corporate Law:**
    - Vodafone International Holdings v. Union of India (2012) - Tax jurisdiction
    - Satyam Computer Services fraud case (2009) - Corporate governance
    
    Click any category to search for related cases!
    """
    )

# Statistics
if "recent_searches" in st.session_state and st.session_state.recent_searches:
    st.markdown("---")
    st.subheader("📊 Your Search Activity")

    stats_col1, stats_col2 = st.columns(2)

    with stats_col1:
        st.metric("Total Searches", len(st.session_state.recent_searches))

    with stats_col2:
        st.metric("Recent Searches", len(st.session_state.recent_searches[-5:]))

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666; font-size: 0.85em;">
⚠️ This case search tool uses AI simulation for demonstration purposes.<br>
Always verify case details with official legal databases and consult legal professionals.
</div>
""",
    unsafe_allow_html=True,
)
