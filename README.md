# NutriBaby

AI-powered baby nutrition tracker. Log meals in natural language; get age-appropriate nutrition analysis and gap-filling suggestions.

> **Learning project — not medical advice. Consult your pediatrician.**

## Quick start

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your API keys
cp .env.example .env
# edit .env and paste in your ANTHROPIC_API_KEY and USDA_API_KEY

# 4. Run the app
streamlit run app.py
```

## API keys needed

| Key | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `USDA_API_KEY` | https://fdc.nal.usda.gov/api-key-signup |
