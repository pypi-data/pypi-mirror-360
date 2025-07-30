# Handy Utilities with Streamlit

> Collection Of Utilities For Daily Life Hacks

## Usage

### Run Directly with `uv`

```bash
uvx k-utils
```

### Install Locally

```bash
git clone https://github.com/hoishing/handy-uti.git
cd k-utils
uv sync  # install dependencies with uv
source .venv/bin/activate
streamlit run k_utils/main.py
```

## API Keys

- Create a `.env` file in the project root with your API keys (optional)
- api key fields in the app will be auto-filled after adding the secret file

```env
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
MISTRAL_API_KEY=your-mistral-api-key
```

API key fields in the app will be auto-filled after adding the .env file.

## Questions?

Open a [github issue] or ping me on [LinkedIn]

[github issue]: https://github.com/hoishing/handy-utils/issues
[LinkedIn]: https://www.linkedin.com/in/kng2
