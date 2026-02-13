# IQ Finance - Company Intelligence Dashboard

AI-powered B2B company intelligence platform with beautiful Evidence.dev-inspired UI.

## Features

- 🚀 Real-time company enrichment
- 🎨 Beautiful gradient UI design
- 🤖 DeepSeek R1 AI analysis
- 💰 Ultra-low cost ($0.004/company)
- ⚡ Fast (~30 second analysis)

## Deployment

### Streamlit Cloud (Recommended)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in Streamlit Cloud settings:
   - `BRAND_API_KEY` = your Brand.dev API key
   - `OPENROUTER_API_KEY` = your OpenRouter API key
5. Deploy!

### Local Development

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Configuration

Set environment variables or add to Streamlit secrets:

- `BRAND_API_KEY` - Brand.dev API key (optional, has graceful fallback)
- `OPENROUTER_API_KEY` - OpenRouter API key for DeepSeek R1

## Tech Stack

- **Frontend**: Streamlit
- **AI**: DeepSeek R1 via OpenRouter
- **Data**: Brand.dev API, web scraping
- **Design**: Evidence.dev-inspired gradients

## Cost

- **Per company**: ~$0.004
- **Per 1000 companies**: ~$4
- Extremely cost-effective for B2B intelligence

## License

Proprietary - IQ Finance
