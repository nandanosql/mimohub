# 🧠 MiMo Hub

> **Talk to your Excel data using Xiaomi MiMo AI**

MiMo Hub is a Streamlit-powered tool that lets you upload Excel (`.xlsx`, `.xls`) and CSV files, get **instant automated analysis**, and **chat with your data** using Xiaomi's MiMo-V2-Flash AI model.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Instant Analysis** | Auto-generated stats, distributions, and correlations |
| 💬 **Chat with Data** | Ask questions in natural language, get AI answers |
| 🛡️ **Data Quality** | Automatic detection of missing values, duplicates, outliers |
| 📈 **Visualizations** | Histograms, bar charts, and correlation heatmaps |
| 🔑 **BYOK** | Bring Your Own Key — your API key stays on your machine |

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-username/mimohub.git
cd mimohub
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API key

Copy the example env file and add your key:

```bash
cp .env.example .env
```

Edit `.env` and set your Xiaomi MiMo API key:

```
XIAOMI_MIMO_API_KEY=sk-your-key-here
```

> 💡 You can also enter your key directly in the app sidebar (BYOK).

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🗂️ Project Structure

```
mimohub/
├── .streamlit/
│   └── config.toml          # Streamlit theme config
├── assets/
│   └── styles.css            # Custom CSS styles
├── utils/
│   ├── __init__.py
│   ├── excel_processor.py    # Data loading, stats, quality checks
│   └── mimo_client.py        # MiMo AI chat integration via LiteLLM
├── .env.example              # Environment variable template
├── app.py                    # Main Streamlit application
└── requirements.txt          # Python dependencies
```

---

## 📦 Dependencies

- **[Streamlit](https://streamlit.io/)** — App framework
- **[Pandas](https://pandas.pydata.org/)** — Data manipulation
- **[Plotly](https://plotly.com/python/)** — Interactive visualizations
- **[LiteLLM](https://github.com/BerriAI/litellm)** — Unified LLM API client
- **[OpenPyXL](https://openpyxl.readthedocs.io/)** — Excel file reading
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — Environment variable management

---

## 🔑 Getting an API Key

1. Visit [platform.xiaomimimo.com](https://platform.xiaomimimo.com)
2. Create a free account
3. Generate an API key
4. Paste it in the app sidebar or `.env` file

---

## 🛡️ Security

- **BYOK (Bring Your Own Key)** — API keys are never stored on the server
- **No data persistence** — uploaded files are processed in-memory only
- **Input validation** — chat messages are sanitized with length limits and rate limiting

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
