# 📝 AI Meeting Minutes & Action Items

Paste raw meeting notes → get an executive summary, action items, risks, and decisions.

Modes:
- **LLM mode (Gemini 1.5 Flash)** — requires `GEMINI_API_KEY` in Streamlit Secrets  
- **Demo mode** — works without any key (rule-based extraction)

## Run locally

## Deploy (Streamlit Cloud)
- Connect GitHub repo, set file path to `app.py`
- Add a secret under Settings → Secrets:
  `GEMINI_API_KEY = "your-key"`
