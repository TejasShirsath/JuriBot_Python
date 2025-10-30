"""
Cost Estimator Page
Legal cost estimation tool with AI-enhanced reasoning
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from utils.gemini_flash import get_gemini_client
from utils.db_utils import get_db

st.set_page_config(page_title="Cost Estimator - JuriBot", page_icon="💰", layout="wide")

# Initialize
db = get_db()
gemini = get_gemini_client()

st.title("💰 Legal Cost Estimator")
st.markdown("Estimate legal costs for your case with AI-powered insights")

# Sidebar
with st.sidebar:
    st.header("⚙️ Estimation Settings")

    # Case details
    case_type = st.selectbox(
        "Case Type",
        [
            "Civil Litigation",
            "Criminal Defense",
            "Corporate/Commercial",
            "Property Dispute",
            "Family Law",
            "Consumer Protection",
            "Labor/Employment",
            "Tax Litigation",
            "Intellectual Property",
            "Arbitration",
        ],
    )

    location = st.selectbox(
        "Location/Jurisdiction",
        [
            "Delhi",
            "Mumbai",
            "Bangalore",
            "Kolkata",
            "Chennai",
            "Hyderabad",
            "Pune",
            "Ahmedabad",
            "Tier-2 City",
            "Tier-3 City",
        ],
    )

    complexity = st.select_slider(
        "Case Complexity",
        options=["Low", "Medium", "High", "Very High"],
        value="Medium",
    )

    court_level = st.selectbox(
        "Court Level",
        [
            "District Court",
            "High Court",
            "Supreme Court",
            "Tribunal",
            "Out of Court Settlement",
        ],
    )

    duration_months = st.slider(
        "Expected Duration (months)", min_value=1, max_value=60, value=12
    )

    st.markdown("---")

    # Additional factors
    st.subheader("Additional Factors")

    has_expert_witness = st.checkbox("Expert Witness Required")
    has_document_review = st.checkbox("Extensive Document Review")
    has_travel = st.checkbox("Travel Required")
    has_appeals = st.checkbox("Appeals Expected")

# Main content


# Quick estimates (rule-based)
def calculate_base_cost(case_type, location, complexity, court_level):
    """Calculate baseline cost using fixed rules"""

    # Base rates by case type (in INR)
    base_rates = {
        "Civil Litigation": 50000,
        "Criminal Defense": 75000,
        "Corporate/Commercial": 100000,
        "Property Dispute": 60000,
        "Family Law": 40000,
        "Consumer Protection": 30000,
        "Labor/Employment": 45000,
        "Tax Litigation": 80000,
        "Intellectual Property": 90000,
        "Arbitration": 120000,
    }

    # Location multipliers
    location_multipliers = {
        "Delhi": 1.3,
        "Mumbai": 1.4,
        "Bangalore": 1.2,
        "Kolkata": 1.1,
        "Chennai": 1.15,
        "Hyderabad": 1.1,
        "Pune": 1.1,
        "Ahmedabad": 1.0,
        "Tier-2 City": 0.8,
        "Tier-3 City": 0.6,
    }

    # Complexity multipliers
    complexity_multipliers = {"Low": 0.7, "Medium": 1.0, "High": 1.5, "Very High": 2.0}

    # Court level multipliers
    court_multipliers = {
        "District Court": 1.0,
        "High Court": 1.5,
        "Supreme Court": 2.5,
        "Tribunal": 0.8,
        "Out of Court Settlement": 0.6,
    }

    base = base_rates.get(case_type, 50000)
    location_mult = location_multipliers.get(location, 1.0)
    complexity_mult = complexity_multipliers.get(complexity, 1.0)
    court_mult = court_multipliers.get(court_level, 1.0)

    return base * location_mult * complexity_mult * court_mult


st.subheader("📋 Case Details Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Type:** {case_type}")
    st.info(f"**Location:** {location}")

with col2:
    st.info(f"**Complexity:** {complexity}")
    st.info(f"**Court:** {court_level}")

with col3:
    st.info(f"**Duration:** {duration_months} months")
    factors = []
    if has_expert_witness:
        factors.append("Expert Witness")
    if has_document_review:
        factors.append("Document Review")
    if has_travel:
        factors.append("Travel")
    if has_appeals:
        factors.append("Appeals")
    st.info(f"**Factors:** {', '.join(factors) if factors else 'None'}")

# Additional details
st.subheader("📝 Additional Case Details")

case_details = st.text_area(
    "Describe your case (optional)",
    placeholder="Provide any additional details about your case that might affect costs...",
    height=100,
    help="More details help provide better estimates",
)

# Estimate button
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    estimate_button = st.button(
        "💡 Calculate Cost Estimate", type="primary", use_container_width=True
    )

if estimate_button:

    with st.spinner("Calculating cost estimate..."):

        # Calculate base cost
        base_cost = calculate_base_cost(case_type, location, complexity, court_level)

        # Apply additional factors
        additional_cost = 0

        if has_expert_witness:
            additional_cost += base_cost * 0.15
        if has_document_review:
            additional_cost += base_cost * 0.10
        if has_travel:
            additional_cost += base_cost * 0.08
        if has_appeals:
            additional_cost += base_cost * 0.25

        # Duration factor
        duration_factor = duration_months / 12
        total_estimated = (base_cost + additional_cost) * duration_factor

        # Create range (±20%)
        min_estimate = total_estimated * 0.8
        max_estimate = total_estimated * 1.2

        # Store results
        st.session_state.cost_estimate = {
            "min": min_estimate,
            "max": max_estimate,
            "avg": total_estimated,
            "base": base_cost,
            "additional": additional_cost,
        }

        # Get AI-enhanced analysis if available
        if gemini:
            with st.spinner("Getting AI-enhanced insights..."):
                ai_analysis = gemini.estimate_legal_costs(
                    case_type=case_type,
                    location=location,
                    complexity=complexity,
                    details=case_details,
                )
                st.session_state.ai_analysis = ai_analysis

                # Store in database
                db.add_cost_estimate(
                    case_type=case_type,
                    location=location,
                    complexity=complexity,
                    estimated_cost=f"₹{min_estimate:,.0f} - ₹{max_estimate:,.0f}",
                    details=case_details,
                )

# Display results
if "cost_estimate" in st.session_state:

    st.markdown("---")
    st.subheader("💰 Cost Estimate Results")

    estimate = st.session_state.cost_estimate

    # Main estimate display
    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.metric(
            "Minimum Estimate", f"₹{estimate['min']:,.0f}", help="Conservative estimate"
        )

    with result_col2:
        st.metric(
            "Average Estimate", f"₹{estimate['avg']:,.0f}", help="Most likely cost"
        )

    with result_col3:
        st.metric(
            "Maximum Estimate", f"₹{estimate['max']:,.0f}", help="Upper bound estimate"
        )

    # Cost breakdown visualization
    st.markdown("---")
    st.subheader("📊 Cost Breakdown")

    # Create pie chart
    breakdown_data = {
        "Category": [
            "Base Legal Fees",
            "Court Fees",
            "Documentation",
            "Additional Costs",
        ],
        "Amount": [
            estimate["base"] * 0.6,
            estimate["base"] * 0.15,
            estimate["base"] * 0.15,
            estimate["additional"],
        ],
    }

    fig_pie = px.pie(
        values=breakdown_data["Amount"],
        names=breakdown_data["Category"],
        title="Estimated Cost Distribution",
        hole=0.4,
    )

    fig_pie.update_traces(textposition="inside", textinfo="percent+label")

    st.plotly_chart(fig_pie, use_container_width=True)

    # Range visualization
    fig_range = go.Figure()

    fig_range.add_trace(
        go.Bar(
            x=["Minimum", "Average", "Maximum"],
            y=[estimate["min"], estimate["avg"], estimate["max"]],
            marker_color=["lightgreen", "gold", "lightcoral"],
            text=[
                f"₹{estimate['min']:,.0f}",
                f"₹{estimate['avg']:,.0f}",
                f"₹{estimate['max']:,.0f}",
            ],
            textposition="auto",
        )
    )

    fig_range.update_layout(
        title="Cost Range Estimates",
        xaxis_title="Estimate Type",
        yaxis_title="Amount (INR)",
        showlegend=False,
    )

    st.plotly_chart(fig_range, use_container_width=True)

    # AI Analysis
    if "ai_analysis" in st.session_state:
        st.markdown("---")
        st.subheader("🤖 AI-Enhanced Analysis")

        st.markdown(st.session_state.ai_analysis)

    # Cost optimization tips
    st.markdown("---")
    st.subheader("💡 Cost Optimization Tips")

    tip_col1, tip_col2 = st.columns(2)

    with tip_col1:
        st.markdown(
            """
        **Ways to Reduce Costs:**
        - Consider mediation or arbitration
        - Organize documents beforehand
        - Be responsive to lawyer's requests
        - Consider fixed-fee arrangements
        - Explore legal aid if eligible
        """
        )

    with tip_col2:
        st.markdown(
            """
        **What Increases Costs:**
        - Delays and adjournments
        - Incomplete documentation
        - Multiple court hearings
        - Appeals to higher courts
        - Complex evidence requirements
        """
        )

    # Export option
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        export_data = f"""Legal Cost Estimate Report
{'='*60}

Case Type: {case_type}
Location: {location}
Complexity: {complexity}
Court Level: {court_level}
Expected Duration: {duration_months} months

{'='*60}

COST ESTIMATES:

Minimum: ₹{estimate['min']:,.0f}
Average: ₹{estimate['avg']:,.0f}
Maximum: ₹{estimate['max']:,.0f}

Base Cost: ₹{estimate['base']:,.0f}
Additional Costs: ₹{estimate['additional']:,.0f}

{'='*60}

{st.session_state.get('ai_analysis', '')}

{'='*60}

Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Disclaimer: These are estimated costs for planning purposes only.
Actual costs may vary based on case specifics. Always get a detailed
quote from your lawyer.
"""

        st.download_button(
            label="📥 Download Estimate Report",
            data=export_data,
            file_name=f"cost_estimate_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )

    with col2:
        if st.button("🔄 Calculate New Estimate"):
            del st.session_state.cost_estimate
            if "ai_analysis" in st.session_state:
                del st.session_state.ai_analysis
            st.rerun()

else:
    # Initial state - show typical cost ranges
    st.markdown("---")
    st.subheader("📊 Typical Cost Ranges")

    st.info(
        """
    **General Guidelines for Legal Costs in India:**
    
    - **District Court Civil Cases**: ₹30,000 - ₹2,00,000
    - **High Court Cases**: ₹1,00,000 - ₹10,00,000+
    - **Supreme Court Cases**: ₹5,00,000 - ₹50,00,000+
    - **Arbitration**: ₹2,00,000 - ₹20,00,000+
    - **Corporate Matters**: ₹1,00,000 - ₹50,00,000+
    
    *These ranges vary significantly based on case complexity, duration, and location.*
    """
    )

    st.warning(
        """
    **Important Factors Affecting Costs:**
    
    1. **Lawyer's Experience**: Senior lawyers charge significantly more
    2. **Case Complexity**: More complex cases require more time and expertise
    3. **Court Level**: Higher courts typically mean higher costs
    4. **Location**: Metro cities have higher rates than smaller cities
    5. **Duration**: Longer cases accumulate more fees
    6. **Success Fee**: Some lawyers charge contingency or success fees
    """
    )

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #666; font-size: 0.85em;">
⚠️ These estimates are for informational and planning purposes only.<br>
Actual legal costs depend on many factors. Always get detailed quotes from qualified legal professionals.
</div>
""",
    unsafe_allow_html=True,
)
