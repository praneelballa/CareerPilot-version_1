```markdown
# CareerPilotAI 
An autonomous, end-to-end career intelligence and job application copilot built with **FastAPI**, **React (Vite)**, and **Groq LPU Inference**. 

CareerPilotAI bridges the gap between raw resume data and job discovery by parsing resumes deterministically, running semantic matching against live job descriptions, grounding company research, tailoring application materials, and enforcing a strict human-in-the-loop approval gate for email outreach.

---

## 🌟 Key Features

* **Deterministic & Semantic Resume Parsing**: Extracts structured candidate entities (skills, experience, education, projects) using Groq inference with schema sanitization and normalization.
* **Hybrid Matching Engine**: 
  * Computes mathematical match metrics using sentence embeddings (`all-MiniLM-L6-v2`) for semantic similarity.
  * Calculates explicit skill coverage and geographic/remote compatibility.
  * Generates grounded evidence breakdowns, skill gap analyses, and sequenced career roadmaps via LangGraph agents.
* **Grounded Company Research**: Autonomous pipeline that discovers official company domains, gathers publicly available company data, and neutralizes prompt-injection attempts from untrusted web text.
* **Resume Tailoring & Optimization**: Generates ATS-friendly impact bullets and identifies unproven skill gaps without hallucinating fake credentials.
* **Mandatory Human-in-the-Loop Review Gate**: Protects outbound communications. No email or application package can be dispatched without explicit user verification and cryptographic idempotency checks.

---

## 🛠️ Architecture & Tech Stack

* **Backend**: FastAPI (Python 3.12), Pydantic v2, LangGraph, SQLite (`aiosqlite`)
* **LLM & Inference**: Groq SDK (`openai/gpt-oss-20b`, `qwen/qwen3.8-27b`)
* **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
* **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons
* **Testing**: Pytest, AsyncIO Test Harness (25 tests covering security invariants, matching, and extraction)

---

## 📁 Project Structure

```text
CareerPilotAI/
├── backend/
│   ├── app/
│   │   ├── agents/            # LangGraph workflows & Groq agents
│   │   │   ├── matching_graph.py
│   │   │   ├── resume_parser.py
│   │   │   ├── resume_tailor_agent.py
│   │   │   ├── company_research_graph.py
│   │   │   └── application_agents.py
│   │   ├── api/v1/            # FastAPI REST routes (resumes, jobs, matching, applications)
│   │   ├── schemas/           # Pydantic data models
│   │   ├── services/          # Embeddings, scrapers, normalization, DB access
│   │   ├── config.py          # Application settings & environment variables
│   │   └── main.py            # API entrypoint & CORS configuration
│   ├── tests/                 # Unit & integration test suites
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # API keys and local config
├── frontend/
│   ├── src/                   # React components, stores, and API clients
│   ├── package.json
│   └── vite.config.ts
└── README.md

```

---

## ⚙️ Prerequisites

* **Python**: 3.11 or 3.12
* **Node.js**: v18+ and `npm`
* **Groq API Key**: Obtain a free API key from [Groq Console](https://console.groq.com/keys)

---

## 🚀 Getting Started

### 1. Backend Setup

1. Open a terminal and navigate to `backend`:
```bash
cd backend

```


2. Create and activate a virtual environment:
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

```


```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

```


3. Install dependencies:
```bash
pip install -r requirements.txt

```


4. Configure environment variables in `backend/.env`:
```ini
LLM_PROVIDER="groq"
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL="openai/gpt-oss-20b"

EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2"
DATABASE_URL="sqlite:///./careerpilot.db"
ALLOWED_ORIGINS="http://localhost:5173,[http://127.0.0.1:5173](http://127.0.0.1:5173)"

```


5. Verify test suite:
```bash
pytest -v

```


6. Start the API server:
```bash
uvicorn app.main:app --reload --port 8000

```


*The backend will be available at `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).*

---

### 2. Frontend Setup

1. Open a new terminal and navigate to `frontend`:
```bash
cd frontend

```


2. Install dependencies:
```bash
npm install

```


3. Run the development server:
```bash
npm run dev

```


*The frontend dashboard will be available at `http://localhost:5173`.*

---

## 🧪 Testing Invariants & Quality Assurance

Run the automated test suite from the `backend/` directory:

```bash
pytest -v

```

Key test cases verified:

* **SSRF & Injection Defense**: Untrusted external URLs and prompt-injection artifacts in job descriptions or scraped content are stripped before model processing.
* **Deterministic Matching**: Embeddings and mathematical skill overlaps calculate deterministic percentages before LLM reasoning.
* **Human-in-the-Loop Gate**: Outbound actions (e.g., Gmail sending) fail automatically if the application status is not explicitly set to `HUMAN_APPROVED`.

---
Here is a concise paragraph explaining how the platform works to place directly above your demo video:

---

### How It Works

**CareerPilotAI** operates as an autonomous, multi-agent pipeline designed to eliminate hallucinated qualifications while streamlining the job application lifecycle. 
Upon uploading a resume, the platform parses raw text into a structured schema and indexes candidate attributes alongside live job listings. The core engine applies a
deterministic scoring formula combining dense vector embeddings (`all-MiniLM-L6-v2`) for semantic context with explicit keyword coverage and location compatibility. 
High-scoring opportunities are evaluated through specialized LangGraph agents running high-throughput Groq inference—synthesizing grounded match evidence, targeted resume 
bullet adjustments, and autonomous company research without inventing false experience. Finally, every tailored resume version and outbound outreach email must pass through a strict,
human-in-the-loop review gate before dispatch.

---

#### 🎬 Prototype Walkthrough

```

https://github.com/user-attachments/assets/72e811f7-247f-4166-aa09-f638feaf88b3


```
