<div align="center">

# 🎬 ScriptForge AI

**A full-stack YouTube script writing studio built for content creators.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

</div>

---

## 🌟 Overview

**ScriptForge AI** generates comprehensive YouTube scripts to level up your content creation. It helps you build a solid foundation by generating:

- 🔥 **Hook**: Grabs attention in the first few seconds.
- 🗣️ **Introduction**: Sets the stage for your topic.
- 📖 **Main Content**: Structured points and arguments.
- 🎯 **Call to Action**: Tells viewers what to do next.
- 💡 **Titles**: 5 catchy title ideas.
- 🖼️ **Thumbnail Texts**: 5 punchy text overlays for your thumbnails.

Every script is saved automatically. You can review past scripts, copy them to your clipboard, or export them seamlessly as TXT or PDF!

---

## ✨ Features

- **End-to-End Generation:** Automatically drafts everything from hook to call to action.
- **Smart Ideas:** Get multiple title and thumbnail text ideas.
- **History & Persistence:** Built-in SQLite database automatically saves your generated scripts.
- **Exporting:** Instantly export your final script as `.txt` or `.pdf`.
- **Responsive Dark UI:** A beautiful, distraction-free writing environment.

---

## 🚀 Quick Start

### Prerequisites
Make sure you have Python 3.8+ installed on your machine.

### Installation

1. **Clone the repository** (or navigate to the directory):
   ```bash
   cd "YouTube script writer"
   ```

2. **Set up a virtual environment**:
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start the application**:
   ```powershell
   uvicorn app.main:app --reload
   ```

5. **Open in Browser**:
   Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

> 💡 **Tip:** Interactive API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## 📂 Project Structure

```text
app/
├── main.py                 # FastAPI routes and static app setup
├── database.py             # SQLite schema and query logic
├── models.py               # Pydantic validated API models
├── services/
│   ├── generator.py        # Local script generation engine
│   └── exporter.py         # TXT and PDF builder services
└── static/
    ├── index.html          # Application markup
    ├── styles.css          # Responsive dark UI
    └── app.js              # Frontend state and API calls
data/
└── scripts.db              # Automatically created on first run
```

---

## ⚙️ Configuration

You can customize the application by setting environment variables. 

- `SCRIPT_WRITER_DB_PATH`: Set this to use a custom SQLite file location instead of the default `data/scripts.db`.
