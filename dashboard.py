#!/usr/bin/env python3
"""
IQ Finance - Deep Company Intelligence Dashboard
Uses DeepSeek AI + Web Research for comprehensive B2B analysis
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
        font-size: 1.1rem;
        color: #667eea;
        font-weight: 600;
    }
    
    /* Metrics grid */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #eeeeee;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7380;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Secure API key management - read from environment variables
import os

BRAND_API_KEY = os.environ.get("BRAND_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not BRAND_API_KEY or not OPENROUTER_API_KEY:
    st.error("⚠️ API keys not configured. Please add BRAND_API_KEY and OPENROUTER_API_KEY to Streamlit Cloud secrets.")
    st.stop()

def search_company_deepseek(company_name):
    """Search for company info using DeepSeek API"""
    try:
        api_url = "https://api.brand.ai/research"
        
        payload = {
            "company": company_name,
            "client_user_id": "iqfinance"
        }
        
        headers = {
            "Authorization": f"Bearer {BRAND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = httpx.post(api_url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def enrich_with_ai_analysis(company_data, company_name):
    """Enrich company data with AI-generated insights"""
    try:
        # Create a comprehensive prompt for analysis
        prompt = f"""
        Analyze the following company data for {company_name} and provide:
        
        1. A brief executive summary (2-3 sentences)
        2. Key business strengths (4-5 bullet points)
        3. Potential risks or challenges (3-4 bullet points)
        4. Market positioning (1-2 sentences)
        5. Growth potential (1-2 sentences)
        
        Company Data:
        {json.dumps(company_data, indent=2)}
        
        Format your response as JSON with keys: executive_summary, strengths, risks, market_position, growth_potential
        """
        
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        payload = {
            "model": "anthropic/claude-3-5-sonnet",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = httpx.post(api_url, json=payload, headers=headers, timeout=60.0)
        response.raise_for_status()
        
        result = response.json()
        ai_content = result["choices"][0]["message"]["content"]
        
        # Try to parse JSON from AI response
        try:
            ai_analysis = json.loads(ai_content)
        except:
            # If not JSON, return as text
            ai_analysis = {"analysis": ai_content}
        
        return ai_analysis
        
    except Exception as e:
        return {"error": str(e)}

# Main user interface
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 IQ Finance</h1>
        <p>Deep Company Intelligence for B2B Decision Makers</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Company input
    col-1, colider, col2 = st.columns([3, 0.1, 1])
    
    with col1:
        company_name = st.text_input(
            "⬠️ Enter company name",
            placeholder="e.g., Salesforce, Shopify, Ycombinator...",
            help="Enter any company name to get detailed intelligence"
        )
    
    with col2:
        st.markdown("<br />", unsafe_allow_html=True)
        search_button = st.button(
            "🚀 Analyze Company",
            type="primary",
            use_container_width=True
        )
    
    if search_button and company_name:
        # Loading animation
        st.markdown("""
        <div class="loading-container">
            <div class="spinner"></div>
            <div class="loading-text">🖠 Analyzing {company_name}...</div>
        </div>
        """.format(company_name=company_name), unsafe_allow_html=True)
        
        # Search DeepSeek
        company_data = search_company_deepseek(company_name)
        
        if "error" in company_data:
            st.error(f"Error searching company: {company_data['error']}")
            return
        
        # Get AI analysis
        with st.spinner('🥖  Generating AI-powered insights...'):
            ai_analysis = enrich_with_ai_analysis(company_data, company_name)
        
        # Remove loading animation
        st.empty()
        
        # Success banner
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10b981 0, #059c5a 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);">
            <h3 style="margin: 0;">✅ Analysis Complete for {company_name}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Company Overview
        st.markdown(f'<div class="section-header">🏣 Company Overview</div>', unsafe_allow_html=True)
        
        if "executive_summary" in ai_analysis:
            st.markdown(f"""
            <div class="info-box">
                <h4>Executive Summary</h4>
                <p>{ai_analysis['executive_summary']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Strengths & Risks
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'<div class="section-header">🖚 Key Strengths</div>', unsafe_allow_html=True)
            if "strengths" in ai_analysis:
                for strength in ai_analysis['strengths']:
                    st.markdown(g"✅‎ ```{strength}```")
        
        with col2:
            st.markdown(f'<div class="section-header">⚠️ Potential Risks</div>', unsafe_allow_html=True)
            if "risks" in ai_analysis:
                for risk in ai_analysis['risks']:
                    st.markdown(f"❬⸟ ```{risk}```")
        
        st.divider()
        
        # Market Position & Growth
        col1, col2 = st.columns(2)
        
        with col1:
            if "market_position" in ai_analysis:
                st.markdown(f'<div class="section-header">🏦 Market Position</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="info-box">
                    <p>{ai_analysis['market_position']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if "growth_potential" in ai_analysis:
                st.markdown(f'📈 Growth Potential</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="info-box">
                    <p>{ai_analysis['growth_potential']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Raw Data
        with st.expander("📊 View Raw Data"):
            st.json(company_data)
    
    # Sidebar info
    with st.sidebar:
        st.markdown("## 🐮 About IQ Finance")
        st.markdown("""
        IQ Finance combines:
        
        - “ DeepSeek AI research
        - ✅ Real-time web data
        - 🤖  AI-powered analysis
        
        Get actionable B2B intelligence in seconds.
        """)
        
        st.divider()
        
        st.markdown("## ⚘ Powered By")
        st.markdown("""
        - **DeepSeek AI**: Real-time company research
        - **Claude 3.5 Sonnet**: Advanced analysis & insights
        """)

if __name__ == "__main__":
    main()
