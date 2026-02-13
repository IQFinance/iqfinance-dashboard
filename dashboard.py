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
        color: #667eea;
        font-weight: 700;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('''
<div class="main-header">
    <h1>🚀 IQ Finance | Company Intelligence</h1>
    <p>Deep company research powered by DeepSeek AI + Web Research</p>
</div>
''', unsafe_allow_html=True)

# Get API credentials from Streamlit secrets (deployed) or env vars (local)
try:
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
    PERPLEXITY_API_KEY = st.secrets.get("PERPLEXITY_API_KEY")  # Optional
except KeyError:
    st.error("⚠️ **API Keys Not Configured**")
    st.info("""
    Please add your API keys to:
    - `.streamlit/secrets.toml` (local)
    - Streamlit Cloud Secrets (when deployed)
    
    Example `secrets.toml`:
    ```toml
    DEEPSEEK_API_KEY = "your-deepseek-api-key"
    PERPLEXITY_API_KEY = "your-perplexity-api-key"  # optional
    ```
    """)
    st.stop()

# Initialize session state
if 'company_data' not in st.session_state:
    st.session_state.company_data = None

def search_deepseek(company_name: str) -> dict:
    """Search for company using DeepSeek AI"""
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a business intelligence assistant. Provide detailed, structured information."},
                {"role": "user", "content": f"""
                Provide a comprehensive analysis of the company "{company_name}" in JSON format with these exact keys:
                
                {{
                    "company_name": "string",
                    "website": "string",
                    "industry": "string",
                    "founded": "string",
                    "headquarters": "string",
                    "employee_count": "string",
                    "funding": "string",
                    "description": "string",
                    "products_services": ["string"],
                    "key_people": ["string"],
                    "recent_news": ["string"],
                    "competitors": ["string"],
                    "tech_stack": ["string"]
                }}
                
                Include only the JSON object without any explanation.
                """}
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        return json.loads(content)
        
    except Exception as e:
        return {"error": str(e)}

def get_web_research(company_name: str) -> dict:
    """Get additional web research using Perplexity AI (if configured)"""
    if not PERPLEXITY_API_KEY:
        return {"note": "Perplexity API not configured"}
        
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "sonar-small-online",
            "messages": [
                {"role": "system", "content": "Provide the latest information about the company."},
                {"role": "user", "content": f"What are the latest news and updates about {company_name}?"}
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}"
        }
        
        response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        
        result = response.json()
        return {
            "content": result["choices"][0]["message"]["content"],
            "citations": result.get("citations", [])
        }
        
    except Exception as e:
        return {"error": str(e)}

# Sidebar
with st.sidebar:
    st.markdown("## 🔍 Research")
    
    company_name = st.text_input(
        "Company Name",
        placeholder="e.g., Stripe, AirBnB, Figma",
        help="Enter any company name to analyze"
    )
    
    if st.button("🔥 Start Analysis", type="primary", use_container_width=True):
        if not company_name:
            st.warning("⚠ Please enter a company name")
        else:
            # Loading animation
            st.markdown('''
            <div class="loading-container">
                <div class="spinner"></div>
                <div class="loading-text">Analyzing {}...</div>
            </div>
            '''.format(company_name), unsafe_allow_html=True)
            
            # Fetch data
            deepseek_data = search_deepseek(company_name)
            
            if "ERROR" not in deepseek_data:
                web_data = get_web_research(company_name)
                st.session_state.company_data = {
                    "deepseek": deepseek_data,
                    "web": web_data
                }
                st.rerun()
            else:
                st.error(f"⚠ Error: {deepseek_data.get('error', 'Unknown error')}")
    
    st.markdown("""
    ---
    ## 💡 About
    This tool uses:
    - 🪐 **DeepSeek AI**: Deep reasoning & analysis
    - 🌎 **Web Research**: Latest news & updates
    """)

# Main content
if st.session_state.company_data:
    data = st.session_state.company_data["deepseek"]
    
    # Company Header Card
    col1, divider, col2 = st.columns([3, 0.1, 1])
    
    with col1:
        st.markdown(f"# {data.get('company_name', 'Unknown')}")
        st.markdown(f"🌐 [{data.get('website', 'N/A')}]({data.get('website', '#')})")
        st.markdown(f"🏭 {data.get('industry', 'N/A')}")
        st.markdown(f"📍 {data.get('headquarters', 'N/A')}")
    
    with col2:
        st.metric("Founded", data.get('founded', 'N/A'))
        st.metric("Employees", data.get('employee_count', 'N/A'))
        st.metric("Funding", data.get('funding', 'N/A'))
    
    # Description
    st.markdown(f"**Overview:** {data.get('description', 'N/A')}")
    
    # Products & Services
    st.markdown("## 🛠 Products & Services")
    for item in data.get('products_services', []):
        st.markdown(f"- ✓{item}")
    
    # Key People
    cola, colb = st.columns(2)
    
    with cola:
        st.markdown("## 👥 Key People")
        for person in data.get('key_people', []):
            st.markdown(f"- 👤 {person}")
    
    with colb:
        st.markdown("## 🎯 Competitors")
        for comp in data.get('competitors', []):
            st.markdown(f"- 🎯 {comp}")
    
    # Tech Stack
    st.markdown("## 💻 Tech Stack")
    st.write(data.get('tech_stack', []))
    
    # Recent News
    st.markdown("## 📰 Recent News")
    for news in data.get('recent_news', []):
        st.info(news)
    
    # Web Research (if available)
    if st.session_state.company_data.get("web") and "content" in st.session_state.company_data["web"]:
        st.markdown("## 🌐 Latest Web Updates")
        st.markdown(st.session_state.company_data["web"]["content"])
        
        if st.session_state.company_data["web"].get("citations"):
            st.markdown("**Sources:**")
            for cite in st.session_state.company_data["web"]["citations"]:
                st.markdown(f"- [{cite}]({cite})")
else:
    st.markdown("""
    <div class="info-box">
        <h4>👈 Start by entering a company name</h4>
        <p>Enter any company name in the sidebar to begin your analysis. The system will gather comprehensive intelligence including company overview, key people, competitors, tech stack, and recent news.</p>
    </div>
    """, unsafe_allow_html=True)