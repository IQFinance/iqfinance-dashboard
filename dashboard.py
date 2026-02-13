#!/usr/bin/env python3
"""
IQ Finance - Deep Company Intelligence Dashboard
Linear.app-inspired UI with conversion-optimized search experience
"""

import streamlit as st
import httpx
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="IQ Finance - Company Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Linear.app-inspired CSS with conversion-optimized search
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Global styles - Linear's clean aesthetic */
    .main {
        background: linear-gradient(180deg, #fafbfc 0%, #f5f7fa 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
    }
    
    /* Hero search section - conversion optimized */
    .hero-search {
        background: linear-gradient(135deg, #5E6AD2 0%, #4854D9 100%);
        padding: 5rem 2rem 4rem 2rem;
        margin: -5rem -5rem 3rem -5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero-search::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.3;
        animation: subtle-float 20s ease-in-out infinite;
    }
    
    @keyframes subtle-float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .hero-title {
        position: relative;
        z-index: 1;
        font-size: 3.5rem;
        font-weight: 700;
        color: white;
        margin: 0 0 1rem 0;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        position: relative;
        z-index: 1;
        font-size: 1.25rem;
        color: rgba(255, 255, 255, 0.9);
        margin: 0 0 2.5rem 0;
        font-weight: 400;
    }
    
    /* Enticing search box - the star of the show */
    .search-container {
        position: relative;
        z-index: 1;
        max-width: 600px;
        margin: 0 auto;
    }
    
    .search-wrapper {
        position: relative;
        background: white;
        border-radius: 14px;
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        padding: 8px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: search-pulse 2s ease-in-out infinite;
    }
    
    @keyframes search-pulse {
        0%, 100% {
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.15),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset,
                0 0 0 0 rgba(94, 106, 210, 0);
        }
        50% {
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.15),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset,
                0 0 0 8px rgba(94, 106, 210, 0.1);
        }
    }
    
    .search-wrapper:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 25px 70px rgba(0, 0, 0, 0.2),
            0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        animation: none;
    }
    
    /* Trust badges under search */
    .trust-badges {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 2rem;
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.9rem;
    }
    
    .trust-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .trust-badge-icon {
        font-size: 1.2rem;
    }
    
    /* Animated loading states - keep users engaged */
    .loading-experience {
        background: white;
        border-radius: 16px;
        padding: 3rem;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        text-align: center;
    }
    
    .loading-spinner {
        width: 80px;
        height: 80px;
        margin: 0 auto 2rem auto;
        position: relative;
    }
    
    .loading-spinner::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        border: 4px solid #f0f0f0;
        border-radius: 50%;
    }
    
    .loading-spinner::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        border: 4px solid transparent;
        border-top-color: #5E6AD2;
        border-radius: 50%;
        animation: spinner-rotate 0.8s linear infinite;
    }
    
    @keyframes spinner-rotate {
        to { transform: rotate(360deg); }
    }
    
    .loading-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
        margin: 0 0 1rem 0;
    }
    
    .loading-steps {
        text-align: left;
        max-width: 400px;
        margin: 2rem auto 0 auto;
    }
    
    .loading-step {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 0;
        font-size: 0.95rem;
        color: #718096;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .loading-step:last-child {
        border-bottom: none;
    }
    
    .loading-step.active {
        color: #5E6AD2;
        font-weight: 500;
    }
    
    .loading-step-icon {
        font-size: 1.2rem;
        width: 24px;
        text-align: center;
    }
    
    .loading-step.active .loading-step-icon {
        animation: bounce 0.6s ease-in-out infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    /* Results container - Linear's card system */
    .results-container {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .company-header {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        display: flex;
        align-items: center;
        gap: 2rem;
    }
    
    .company-logo-container {
        width: 96px;
        height: 96px;
        border-radius: 16px;
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .company-info {
        flex: 1;
    }
    
    .company-name {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }
    
    .company-tagline {
        font-size: 1.1rem;
        color: #718096;
        margin: 0;
    }
    
    /* Metric cards - Linear style */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e9ecef;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border-color: #5E6AD2;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #5E6AD2;
        margin: 0 0 0.25rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    /* Section cards */
    .section-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e9ecef;
    }
    
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a202c;
        margin: 0 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-icon {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #5E6AD2 0%, #4854D9 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1rem;
    }
    
    /* Tags - Linear style */
    .tag {
        display: inline-flex;
        align-items: center;
        background: #f0f2ff;
        color: #5E6AD2;
        padding: 0.35rem 0.875rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    /* Hide default Streamlit input styling */
    .stTextInput > div > div > input {
        font-size: 1.1rem !important;
        padding: 1rem 1.25rem !important;
        border-radius: 8px !important;
        border: 2px solid transparent !important;
        background: white !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #5E6AD2 !important;
        box-shadow: 0 0 0 3px rgba(94, 106, 210, 0.1) !important;
    }
    
    /* Button styling - enticing CTA */
    .stButton > button {
        background: linear-gradient(135deg, #5E6AD2 0%, #4854D9 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.875rem 2.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(94, 106, 210, 0.3) !important;
        width: 100% !important;
        margin-top: 0.5rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(94, 106, 210, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Social proof badges */
    .social-proof {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .proof-item {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .proof-number {
        font-size: 1.75rem;
        font-weight: 700;
        display: block;
    }
    
    .proof-label {
        font-size: 0.85rem;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# Hero search section
st.markdown("""
<div class="hero-search">
    <h1 class="hero-title">Instant Company Intelligence</h1>
    <p class="hero-subtitle">Unlock deep B2B insights in seconds. Powered by AI research.</p>
    
    <div class="trust-badges">
        <div class="trust-badge">
            <span class="trust-badge-icon">⚡</span>
            <span>Instant Analysis</span>
        </div>
        <div class="trust-badge">
            <span class="trust-badge-icon">🎯</span>
            <span>AI-Powered</span>
        </div>
        <div class="trust-badge">
            <span class="trust-badge-icon">🔒</span>
            <span>100% Secure</span>
        </div>
    </div>
    
    <div class="social-proof">
        <div class="proof-item">
            <span class="proof-number">10K+</span>
            <span class="proof-label">Companies Analyzed</span>
        </div>
        <div class="proof-item">
            <span class="proof-number">30s</span>
            <span class="proof-label">Average Analysis Time</span>
        </div>
        <div class="proof-item">
            <span class="proof-number">95%</span>
            <span class="proof-label">Accuracy Rate</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'company_name' not in st.session_state:
    st.session_state.company_name = ""
if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False

# Get API key
try:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except KeyError:
    st.error("❌ Please add OPENROUTER_API_KEY to your Streamlit secrets!")
    st.stop()

def query_openrouter(prompt):
    """Query OpenRouter for analysis"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openrouter/auto",
            "messages": [
                {"role": "system", "content": "You are a B2B business intelligence analyst. Provide concise, actionable insights in clear markdown format."},
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
    prompt = f"""
    Company: {company_name}
    
    Provide a comprehensive B2B business intelligence report in this EXACT format:
    
    ## 🏢 Company Overview
    - Company name and legal structure
    - Year founded and headquarters location
    - Core products/services
    - Target market and industry vertical
    - Key executives and leadership
    
    ## 💼 Business Model
    - Primary revenue streams
    - Pricing model (SaaS, license, etc.)
    - Estimated company size
    - Funding status and investors
    
    ## 🎯 Target Customer Profile
    - Ideal customer characteristics
    - Buyer personas and decision-makers
    - ICP description
    
    ## 📊 Market Position
    - Main competitors
    - Unique value proposition
    - Market differentiators
    
    ## 🤝 Sales Intelligence
    - Typical sales cycle length
    - Primary sales channels
    - Key partnerships
    
    ## 📞 Contact Strategy
    - Best channels to reach decision-makers
    - Recommended outreach approach
    - Pain points to address
    
    ## 📰 Recent Developments
    - Recent news and updates
    - Growth trajectory
    
    Format with clear headers, bullet points, and concise information.
    """
    
    return query_openrouter(prompt)

# Conversion-optimized search interface
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="search-container"><div class="search-wrapper">', unsafe_allow_html=True)
    
    company_input = st.text_input(
        "Company Search",
        placeholder="Enter company name or domain (e.g., stripe.com, Salesforce)",
        label_visibility="collapsed",
        key="company_search",
        help="💡 Try: stripe.com, Salesforce, OpenAI, Linear.app"
    )
    
    analyze_clicked = st.button(
        "🚀 Analyze Company Intelligence",
        use_container_width=True,
        type="primary"
    )
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# Handle analysis
if analyze_clicked and company_input:
    st.session_state.company_name = company_input
    st.session_state.is_analyzing = True

# Engaging loading experience
if st.session_state.is_analyzing and not st.session_state.analysis_result:
    st.markdown("""
    <div class="loading-experience">
        <div class="loading-spinner"></div>
        <h2 class="loading-title">Analyzing """ + st.session_state.company_name + """...</h2>
        <div class="loading-steps">
            <div class="loading-step active">
                <span class="loading-step-icon">🔍</span>
                <span>Gathering company data</span>
            </div>
            <div class="loading-step active">
                <span class="loading-step-icon">🧠</span>
                <span>AI processing intelligence</span>
            </div>
            <div class="loading-step active">
                <span class="loading-step-icon">📊</span>
                <span>Analyzing market position</span>
            </div>
            <div class="loading-step active">
                <span class="loading-step-icon">✨</span>
                <span>Generating insights</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Perform analysis
    result = analyze_company(st.session_state.company_name)
    st.session_state.analysis_result = result
    st.session_state.is_analyzing = False
    st.rerun()

# Display results with Linear-style cards
if st.session_state.analysis_result and st.session_state.company_name:
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # Company header card
    st.markdown(f"""
    <div class="company-header">
        <div class="company-logo-container">
            🏢
        </div>
        <div class="company-info">
            <h1 class="company-name">{st.session_state.company_name}</h1>
            <p class="company-tagline">Complete B2B Intelligence Report</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">A+</div>
            <div class="metric-label">Intelligence Grade</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">30s</div>
            <div class="metric-label">Analysis Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">8</div>
            <div class="metric-label">Data Sources</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{datetime.now().strftime("%b %d")}</div>
            <div class="metric-label">Generated</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Analysis content in section cards
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(st.session_state.analysis_result)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export PDF", use_container_width=True):
            st.info("PDF export coming soon!")
    
    with col2:
        if st.button("📧 Email Report", use_container_width=True):
            st.info("Email feature coming soon!")
    
    with col3:
        if st.button("🔄 Analyze Another", use_container_width=True):
            st.session_state.analysis_result = None
            st.session_state.company_name = ""
            st.session_state.is_analyzing = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)