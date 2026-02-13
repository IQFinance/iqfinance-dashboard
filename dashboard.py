#!/usr/bin/env python3
"""
IQ Finance - Deep Company Intelligence Dashboard
Uses OpenRouter AI + Web Research for comprehensive B2B analysis
"""

import streamlit as st
import httpx
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="IQ Finance - Company Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Evidence.dev-style beautiful UI
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main gradient header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    .main-header p {
        margin-top: 0.5rem;
        font-size: 1.2rem;
        opacity: 0.95;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 15px;
        margin: 2rem 0;
    }
    
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        margin-top: 1.5rem;
        font-size: 1.1rem;
        color: #667eea;
        font-weight: 600;
    }
    
    /* Company card */
    .company-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
    }
    
    .company-logo {
        width: 80px;
        height: 80px;
        border-radius: 12px;
        margin-bottom: 1rem;
        object-fit: contain;
        background: white;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a202c;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #f6f9fc 0%, #f1f5f9 100%);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box h4 {
        margin: 0 0 0.5rem 0;
        color: #667eea;
        font-weight: 700;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.06);
        text-align: center;
        margin: 1rem 0;
    }
    
    .metric-card h3 {
        color: #667eea;
        font-size: 2.5rem;
        margin: 0 0 0.5rem 0;
    }
    
    .metric-card p {
        color: #6c7080;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Tags */
    .tag {
        display: inline-block;
        background: #eef2ff;
        color: #667eea;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('''
<div class="main-header">
    <h1>🚀 IQ Finance</h1>
    <p>Deep Company Intelligence - Instant B2B Analysis</p>
</div>
''', unsafe_allow_html=True)

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Get API key
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except KeyError:
    st.error("❌ Please add OPENROUTER_API_KEY to your Streamlit secrets!")
    st.info("Go to Streamlit Cloud → App Settings → Secrets and add:\n```\nOPENROUTER_API_KEY=\"your-openrouter-key\"\n```")
    st.stop()

# Optional: Perplexity key for advanced web search (fallback to free search if not provided)
try:
    PERPLEXITY_API_KEY = st.secrets.get("PERPLEXITY_API_KEY", None)
except KeyError:
    PERPLEXITY_API_KEY = None

def query_openrouter(prompt):
    """Query OpenRouter for analysis only, no web research"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openrouter/auto",
            "messages": [
                {"role": "system", "content": "You are a B2B business intelligence analyst. Provide concise, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_company(company_name):
    """Generate comprehensive company analysis"""
    with st.spinner(f"✨ Analyzing {company_name} with AI..."):
        prompt = f"""
        Company: {company_name}
        
        Provide a comprehensive B2B business intelligence report:
        
        ## Company Overview
        - Company name and legal structure
        - Year founded and headquarters location
        - Core product/s/service(s)
        - Target market and industry vertical
        - Key executives and leadership
        
        ## Business Model
        - Primary revenue streams
        - Pricing model (SaaS, license, one-time, etc.)
        - Estimated company size (employees, revenue if known)
        - Funding status and investors
        
        ## Target Customer Profile
        - Ideal customer characteristics
        - Buyer personas and decision-makers
        - ICP (Ideal Customer Profile) description
        
        ## Market Position
        - Main competitors
        - Unique value proposition
        - Market differentiators and competitive advantages
        
        ## Sales Intelligence
        - Typical sales cycle length
        - Primary sales channels (direct, partners, etc.)
        - Key partnerships and integrations
        
        ## Contact & Reach Optimization
        - Best channels to reach decision-makers (linkedin, email, events, etc.)
        - Recommended outreach strategy and messaging angles
        - Potential pain points to address in outreach
        
        ## Recent News & Developments
        - Recent company updates, funding rounds, or product launch
        - Growth trajectory and market expansion
        
        Format the response in very clear Markdown with bold headers, bullet points, and clear sections.
        """
        
        result = query_openrouter(prompt)
        return result

# Sidebar - Company Input
with st.sidebar:
    st.header("🔍‍💻 Company Search")
    company_name = st.text_input(
        "Enter Company Name",
        placeholder="e.g., Acme Corp or acmecorp.com",
        help="Enter a company name or website to get detailed B2B intelligence"
    )
    
    analyze_button = st.button(
        "🚀 Analyze Company", 
        disabled=(not company_name)
    )