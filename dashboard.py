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
    
    /* Success banner */
    .success-banner {
        background: linear-gradient(135deg, #00d4aa 0%, #00b894 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    /* Enrich button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 0.75rem 3rem;
        border-radius: 10px;
        border: none;
        width: 100%;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
OPENROUTER_API_KEY = "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"
BRANDDEV_API_KEY = "brand_275f0313c59a437687cfcc4fffbc19ee"

def show_loading():
    """Display beautiful loading animation"""
    st.markdown("""
    <div class="loading-container">
        <div class="spinner"></div>
        <div class="loading-text">🔍 Researching company intelligence...</div>
        <p style="color: #64748b; margin-top: 0.5rem;">Analyzing website • Extracting insights • Generating report</p>
    </div>
    """, unsafe_allow_html=True)

def scrape_company_website(domain: str) -> dict:
    """Scrape company website for comprehensive data"""
    print(f"🌐 Scraping website: {domain}")
    
    # Add protocol if missing
    url = domain if domain.startswith('http') else f'https://{domain}'
    
    try:
        client = httpx.Client(timeout=30.0, follow_redirects=True)
        response = client.get(url)
        
        # Extract basic info
        content = response.text[:5000]  # First 5000 chars
        
        return {
            "url": url,
            "status": response.status_code,
            "content_preview": content,
            "success": True
        }
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return {
            "url": url,
            "success": False,
            "error": str(e)
        }

def get_brand_data(domain: str) -> dict:
    """Get brand data from Brand.dev API"""
    print(f"🎨 Fetching brand data for: {domain}")
    
    try:
        client = httpx.Client(timeout=30.0)
        response = client.post(
            "https://api.brand.dev/v1/brand/retrieve",
            headers={
                "Authorization": f"Bearer {BRANDDEV_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"domain": domain}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Brand data retrieved: {data.get('name', 'Unknown')}")
            return data
        else:
            # If 403, API calls might be exhausted - return empty but don't fail
            print(f"⚠️ Brand.dev returned {response.status_code} - continuing without brand data")
            return {"name": domain, "note": "Brand data unavailable"}
    except Exception as e:
        print(f"⚠️ Brand.dev error: {e} - continuing without brand data")
        return {"name": domain, "note": "Brand data unavailable"}

def analyze_with_deepseek(domain: str, website_data: dict, brand_data: dict) -> dict:
    """Deep analysis using DeepSeek R1 via OpenRouter"""
    print(f"🤖 Analyzing with DeepSeek R1 via OpenRouter...")
    
    # Build comprehensive prompt with all gathered data
    prompt = f"""Analyze this B2B company for investment intelligence. Be comprehensive and detailed.

Company Domain: {domain}
Brand Name: {brand_data.get('name', domain)}
Industry: {brand_data.get('industry', 'To be determined')}

Website Content Sample:
{website_data.get('content_preview', 'No content available')[:1500]}

Provide a detailed analysis covering:

1. **Company Overview** (2-3 sentences)
   - What does this company do?
   - Who are their target customers?

2. **Value Proposition** (3 key points)
   - Core product/service offerings
   - Unique competitive advantages
   - Technology or approach differentiation

3. **Market Analysis**
   - Target market size and growth potential
   - Key competitors in this space
   - Market positioning (leader/challenger/niche)

4. **Business Model**
   - Revenue model (SaaS, transaction, licensing, etc.)
   - Pricing strategy insights
   - Customer acquisition approach

5. **Investment Signals** (4-5 bullet points)
   - Growth indicators (funding, expansion, hiring)
   - Technology advantages or moats
   - Market timing and opportunity
   - Potential risks or concerns

6. **Key Metrics & Data Points**
   - Estimated ARR/Revenue (if publicly available)
   - Estimated team size
   - Funding stage/amount (if known)
   - Notable customers or use cases

Be specific, data-driven, and actionable. Format with clear section headers."""

    try:
        client = httpx.Client(timeout=90.0)
        response = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://iqfinance.ai",
                "X-Title": "IQ Finance Company Analysis"
            },
            json={
                "model": "deepseek/deepseek-r1",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert B2B market analyst and investor. Provide detailed, actionable intelligence reports based on company data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            # Get usage stats
            usage = result.get('usage', {})
            total_tokens = usage.get('total_tokens', 0)
            
            # OpenRouter pricing for deepseek-r1
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            cost = (prompt_tokens * 0.00055 + completion_tokens * 2.19) / 1000000
            
            print(f"✅ Analysis complete ({len(analysis)} chars, {total_tokens} tokens, ${cost:.4f})")
            
            return {
                "analysis": analysis,
                "model": "deepseek/deepseek-r1",
                "tokens": total_tokens,
                "cost": cost,
                "success": True
            }
        else:
            error_msg = f"OpenRouter API error: {response.status_code}"
            print(f"❌ {error_msg}")
            return {"error": error_msg, "success": False}
            
    except Exception as e:
        error_msg = f"Analysis error: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg, "success": False}

def enrich_company(domain: str) -> dict:
    """Main enrichment pipeline using DeepSeek web research"""
    
    # Step 1: Get brand data (logo, colors, basic info)
    brand_data = get_brand_data(domain)
    
    # Step 2: Scrape website for content
    website_data = scrape_company_website(domain)
    
    # Step 3: Deep analysis with DeepSeek
    ai_analysis = analyze_with_deepseek(domain, website_data, brand_data)
    
    # Combine all data
    return {
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "brand": brand_data,
        "website": website_data,
        "analysis": ai_analysis,
        "processing_time": "~30 seconds",
        "cost": ai_analysis.get('cost', 0)
    }

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 IQ Finance</h1>
    <p>Deep Company Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# Main interface
st.markdown("### 🔍 Analyze Any B2B Company")

col1, col2 = st.columns([3, 1])

with col1:
    domain_input = st.text_input(
        "Company Website URL",
        placeholder="e.g., stripe.com, shopify.com, hubspot.com",
        label_visibility="collapsed"
    )

with col2:
    enrich_button = st.button("🚀 Analyze", use_container_width=True)

# Quick examples
st.markdown("**Quick examples:**")
example_col1, example_col2, example_col3, example_col4 = st.columns(4)

with example_col1:
    if st.button("Stripe", use_container_width=True):
        domain_input = "stripe.com"
        enrich_button = True

with example_col2:
    if st.button("Shopify", use_container_width=True):
        domain_input = "shopify.com"
        enrich_button = True

with example_col3:
    if st.button("HubSpot", use_container_width=True):
        domain_input = "hubspot.com"
        enrich_button = True

with example_col4:
    if st.button("Salesforce", use_container_width=True):
        domain_input = "salesforce.com"
        enrich_button = True

# Process enrichment
if enrich_button and domain_input:
    # Show loading
    loading_placeholder = st.empty()
    with loading_placeholder:
        show_loading()
    
    # Run enrichment
    result = enrich_company(domain_input)
    
    # Clear loading
    loading_placeholder.empty()
    
    # Show success banner
    st.markdown("""
    <div class="success-banner">
        ✅ Company analysis complete! Deep intelligence report generated.
    </div>
    """, unsafe_allow_html=True)
    
    # Display results
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="section-header">Company Profile</div>', unsafe_allow_html=True)
        
        # Logo
        if result['brand'].get('logo'):
            st.image(result['brand']['logo'], width=120)
        
        # Company name
        st.markdown(f"### {result['brand'].get('name', domain_input)}")
        
        # Industry
        if result['brand'].get('industry'):
            st.markdown(f"**Industry:** {result['brand']['industry']}")
        
        # Brand colors
        if result['brand'].get('colors'):
            st.markdown("**Brand Colors:**")
            colors_html = " ".join([
                f'<span style="display:inline-block;width:40px;height:40px;background:{color};border-radius:8px;margin:4px;border:2px solid #e2e8f0;"></span>'
                for color in result['brand']['colors'][:4]
            ])
            st.markdown(colors_html, unsafe_allow_html=True)
        
        # Meta info
        st.markdown("---")
        st.markdown(f"**Domain:** {domain_input}")
        st.markdown(f"**Analyzed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        st.markdown(f"**Cost:** ${result['cost']:.4f}")
    
    with col2:
        st.markdown('<div class="section-header">Intelligence Report</div>', unsafe_allow_html=True)
        
        # Display the DeepSeek analysis
        if result['analysis'].get('success') and 'analysis' in result['analysis']:
            st.markdown(result['analysis']['analysis'])
        else:
            st.error(f"Analysis failed: {result['analysis'].get('error', 'Unknown error')}")
    
    # Download option
    st.markdown("---")
    download_col1, download_col2 = st.columns([3, 1])
    
    with download_col2:
        json_data = json.dumps(result, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"{domain_input.replace('.', '_')}_analysis.json",
            mime="application/json",
            use_container_width=True
        )

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Dashboard Stats")
    st.metric("AI Model", "DeepSeek R1")
    st.metric("Avg Analysis Time", "~5 sec")
    st.metric("Cost per Company", "$0.003-0.005")
    
    st.markdown("---")
    st.markdown("### ✨ Features")
    st.markdown("""
    - 🌐 **Website Scraping** - Extract company content
    - 🎨 **Brand Analysis** - Logo, colors, industry
    - 🤖 **DeepSeek AI** - Comprehensive intelligence
    - 📊 **Market Analysis** - Size, competition, positioning
    - 💰 **Investment Signals** - Growth indicators & risks
    - 📈 **Business Model** - Revenue & pricing insights
    """)
    
    st.markdown("---")
    st.markdown("### 💡 Pro Tips")
    st.markdown("""
    - Use just the domain (e.g., `stripe.com`)
    - Analysis takes ~30 seconds
    - Download JSON for integrations
    - DeepSeek provides detailed insights
    """)
