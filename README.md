# Question answering System – Natural Language Question Answering System

Question answering System is a question–answering system that extracts factual answers about members from their message history.  
It uses rule-based extraction, keyword retrieval, FastAPI, and optional LLM fallback for descriptive queries.

Architecture and system design reference: :contentReference[oaicite:0]{index=0}  
Setup instructions reference: :contentReference[oaicite:1]{index=1}

---

## ✨ Features

- Member name detection  
- Intent classification (when, where, count, favorites, what, other)  
- Retrieval of top-k relevant messages  
- Rule-based extraction for dates, times, locations, preferences  
- Optional LLM fallback (Ollama)  
- FastAPI server with `/ask` endpoint  
- Deterministic first, then LLM  
- Modular architecture  

---

## 🗂️ Project Structure

# question-answering-system
A hybrid question-answering system for member messages. Uses rule-based extraction for deterministic answers (dates, counts, locations, preferences) and optional LLM fallback for descriptive or vague queries. Built with FastAPI and modular components for retrieval, NLU, and answer extraction.

## 🗂️ Project Structure


member-qa/
│
├── app/
│ ├── main.py
│ ├── client.py
│ ├── nlu.py
│ ├── retrieve.py
│ ├── extract.py
│ ├── llm.py
│ └── init.py
│
├── requirements.txt
└── README.md

yaml
Copy code

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+
- Internet connection for message API
- Optional: Ollama for LLM mode

---

### 2. Download the Project

git clone https://github.com/Prashantanand2811/question-answering-system.git
cd question-answering-system

yaml
Copy code

---

### 3. Create Virtual Environment

**macOS / Linux**
python3 -m venv .venv
source .venv/bin/activate

markdown
Copy code

**Windows**
python -m venv .venv
.venv\Scripts\activate

yaml
Copy code

---

### 4. Install Dependencies

pip install -r requirements.txt

yaml
Copy code

---

### 5. Run API Server

python -m uvicorn app.main:app --reload --port 8000

r
Copy code

Open interactive docs:

http://127.0.0.1:8000/docs

yaml
Copy code

---

### 6. Test API

curl -X POST http://127.0.0.1:8000/ask
-H "Content-Type: application/json"
-d '{"question": "What does Layla prefer?"}'

yaml
Copy code

---

## 🤖 Optional: Enable LLM Mode (Ollama)

### Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

shell
Copy code

### Pull a model
ollama pull llama3

markdown
Copy code

### Enable LLM Mode

**macOS / Linux**
export USE_LLM=true
export OLLAMA_MODEL=llama3

markdown
Copy code

**Windows**
setx USE_LLM "true"
setx OLLAMA_MODEL "llama3"

yaml
Copy code

Restart server:

python -m uvicorn app.main:app --reload --port 8000

yaml
Copy code

---

## 🧠 Pipeline Overview

1. User asks a question  
2. Messages fetched (client.py)  
3. Member + intent detected (nlu.py)  
4. Relevant messages retrieved (retrieve.py)  
5. Rule-based extraction (extract.py)  
6. LLM fallback if needed (llm.py)  
7. JSON answer returned  

Architecture described in detail here: :contentReference[oaicite:2]{index=2}

---

## 🌐 Deployment on Render

1. Push repo to GitHub (already done)  
2. Go to https://render.com → New → Web Service  
3. Connect GitHub repo  

**Build Command**
pip install -r requirements.txt

markdown
Copy code

**Start Command**
uvicorn app.main:app --host 0.0.0.0 --port 10000

yaml
Copy code

4. Deploy  
5. Render provides a public URL

---




---

## 🙌 Contributing

Pull requests are welcome.

---
Prashant Anand
