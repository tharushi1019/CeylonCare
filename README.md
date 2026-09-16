# CeylonCare Health Network — Intelligent Agentic AI System
## IT43212 - Agentic AI | Assignment 2 - Design and Implementation of an Intelligent Agentic AI System for Patient Services Automation | Horizon Campus

> **A production-grade, multi-agent AI system for automating patient services at a private healthcare network across Colombo, Kandy, and Galle, Sri Lanka.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%201.5%20Flash-orange.svg)](https://aistudio.google.com)

---

## System Overview

CeylonCare AI automates five key patient services operations:

| Task | Feature | Agent |
|------|---------|-------|
| 1 | RAG Knowledge Base Q&A (clinic hours, doctors, fees) | `knowledge_agent` |
| 2 | Clinical Symptom Triage & Urgency Assessment | `triage_agent` |
| 3 | Multi-turn Appointment Booking, Cancellation & Reschedule | `appointment_agent` |
| 4 | Patient Visit History & EHR Summarisation | `visit_history_agent` |
| 5 | Emergency Human Escalation (LangGraph HITL interrupt) | `human_escalation_agent` |

---

## Architecture

```
Patient / Operator UI (Streamlit)
          │
          ▼
  [LangGraph StateGraph]
  Entry Router → Supervisor (Gemini + Groq)
                      │
     ┌────────────────┼────────────────┐
     ▼                ▼                ▼
Knowledge Agent   Appointment Agent  Triage Agent
(MiniLM RAG +     (Slot Filling +    (Emergency
 ChromaDB +        Tool Calling)      Detection)
 WHO ICD-11 API)        │                │
                        ▼                ▼
                 Visit History       Human Escalation
                    Agent            Agent (interrupt())
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Primary LLM** | Google Gemini 1.5 Flash (free tier) |
| **Fallback LLM** | Groq (OpenAI-compatible) |
| **Agent Framework** | LangGraph + LangChain (≥ v0.3) |
| **RAG Embeddings** | `all-MiniLM-L6-v2` (HuggingFace) |
| **Vector Database** | ChromaDB |
| **Medical Knowledge** | WHO ICD-11 API + CeylonCare Knowledge Base |
| **ML Risk Predictor** | Random Forest (Scikit-learn, ≥ 90% accuracy) |
| **Vision Triage** | Gemini 1.5 Flash Multimodal + Clinical Heuristics |
| **HITL** | LangGraph `interrupt()` + `Command(resume=...)` |
| **Frontend** | Streamlit ≥ v1.35 |
| **Observability** | LangSmith (optional) + In-app Telemetry |

---

## Features

### Patient Portal
- 🔐 **Secure Login & Registration** (auto-assigns Patient ID)
- ⚡ **1-Click Quick Login** for evaluation/demo access
- 💬 **Multi-turn AI Chat Assistant** with Quick Action Pills
- 📅 **3-Step Visual Booking Wizard** (Branch → Doctor → Date/Time → Confirm)
- 🩺 **Doctor Schedule Lookup** mid-conversation (non-tech friendly)
- 📜 **My Health Records** (appointments, visit history, EHR summary)
- 🖼️ **Multimodal Vision Triage** (upload skin rash/scan/report images)

### Clinical Operator Console
- 🚨 **HITL Emergency Escalation Dashboard** (real-time LangGraph interrupt review)
- 📊 **Predictive Risk & 30-Day Readmission ML Model** (≥ 90% accuracy, 3 clinical presets)
- 📁 **Full Hospital EHR Explorer** (10 patients, Colombo / Kandy / Galle branches)
- 📡 **Live Session Telemetry** with OWASP LLM Top-10 compliance audit

---

## Quick Start — Local Development

### 1. Clone the repository
```bash
git clone https://github.com/<YOUR_USERNAME>/CeylonCare.git
cd CeylonCare
```

### 2. Create virtual environment
```bash
python -m venv .venv
.\.venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 5. Build the RAG Knowledge Base (first run only)
```bash
python build_knowledge_base_minilm.py
```

### 6. Launch the Streamlit app
```bash
streamlit run streamlit_app.py
```

---

## Demo Credentials (for Evaluators & Examiners)

| Role | Quick Login Button | Manual Login |
|------|--------------------|--------------|
| **Patient** | `👤 Log in as Patient (Nimal Perera - P001)` | ID: `P001` / Password: `password123` |
| **Patient 2** | `👤 Log in as Patient (Sunethra Silva - P002)` | ID: `P002` / Password: `password123` |
| **Operator** | `🩺 Log in as Clinical Operator (Sister Kamala)` | Email: `operator@ceyloncare.lk` / Password: `admin` |

---

## Streamlit Community Cloud Deployment

1. **Push this repository to a public GitHub repository** (API keys already excluded via `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New App**
3. Select your repository, branch (`main`), and main file (`streamlit_app.py`)
4. In **Advanced Settings → Secrets**, paste your environment variables:
```toml
GEMINI_API_KEY = "your_actual_key_here"
GROQ_API_KEY = "your_actual_key_here"
WHO_ICD_CLIENT_ID = "your_actual_id_here"
WHO_ICD_CLIENT_SECRET = "your_actual_secret_here"
```
5. Click **Deploy** — the app will build and be live in ~3 minutes.

---

## Hospital Network Coverage

| Branch | City | Emergency 24/7 |
|--------|------|---------------|
| Colombo Central Hospital | Colombo | ✅ Yes |
| Kandy Specialty Center | Kandy | ✅ Yes |
| Galle Coastal Medical Center | Galle | ⚠️ OPD Only |

**13 Specialist Consultants** across Cardiology, General Medicine, Pediatrics, Neurology, Dermatology, Orthopedics, and ENT.

---

## OWASP LLM Safety Compliance

| Risk | Mitigation |
|------|-----------|
| **LLM01: Prompt Injection** | Structured output schema parsing; role-boundary isolation |
| **LLM02: Sensitive Data** | Synthetic PII; local JSON EHR (no cloud DB exposure) |
| **LLM06: Excessive Agency** | All high-risk triage actions gated behind `interrupt()` HITL |
| **LLM09: Overreliance** | Mandatory clinical disclaimers on all diagnostic outputs |

---

## Project Structure

```
CeylonCare/
├── streamlit_app.py              # Main Streamlit application
├── requirements.txt              # Production dependencies
├── .env.example                  # Environment variable template
├── build_knowledge_base_minilm.py  # RAG index builder
│
├── src/
│   ├── graph.py                  # LangGraph StateGraph orchestration
│   ├── supervisor.py             # Supervisor Agent (Gemini + structured output)
│   ├── state.py                  # CeylonCareState TypedDict
│   ├── agents/
│   │   ├── appointment_agent.py  # Multi-turn booking, cancel, reschedule
│   │   ├── knowledge_agent.py    # RAG knowledge Q&A + WHO ICD-11
│   │   ├── triage_agent.py       # Clinical urgency assessment
│   │   ├── visit_history_agent.py
│   │   └── human_escalation_agent.py  # LangGraph interrupt() HITL
│   ├── analytics/
│   │   ├── risk_predictor.py     # Task C: Random Forest ML model
│   │   ├── sentiment_analyzer.py # Task C: NLP priority detection
│   │   └── vision_triage.py      # Task C: Gemini Vision + heuristics
│   ├── rag/
│   │   └── minilm_knowledge_agent.py  # MiniLM + ChromaDB RAG pipeline
│   ├── services/
│   │   └── patient_service.py    # EHR + auth + doctor directory service
│   └── tools/
│       └── patient_tools.py      # LangChain @tool function calling
│
├── data/
│   └── ceyloncare/
│       ├── patients.json          # 10 patient profiles + appointments + visits
│       └── doctors_directory.json # 13 doctors across 3 branches
│
└── knowledge/
    └── clinic_information.txt    # CeylonCare knowledge base (RAG source)
```

---

## Academic References

- [LangGraph Official Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Tool Calling Guide](https://python.langchain.com/docs/how_to/tool_calling/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [HuggingFace Sentence Transformers](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [WHO ICD-11 Classification](https://icd.who.int/en)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [LangSmith Tracing Setup](https://docs.smith.langchain.com/)

---

*© 2026 IT4321 — Agentic AI | Horizon Campus | CeylonCare Health Network (Academic Prototype)*
