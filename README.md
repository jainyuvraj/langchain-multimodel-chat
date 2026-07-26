# ⚡ PolyModel AI - Multi-Model LangChain Chatbot Platform

A production-grade, highly modular multi-model AI chatbot platform built using **Python (FastAPI + LangChain)** and **React (JSX) + Vite** in a single unified monorepo.

Seamlessly switch between **Google Gemini**, **Free Open-Source Models (Llama 3.3, DeepSeek R1, Qwen 2.5, Mixtral)** via Groq, with real-time token streaming, custom parameter tuning, system prompts, and centralized server-side API key management.

---

## 🌟 Current Status & Key Features

### Current Status: **LIVE & OPERATIONAL** 🟢

- **Backend API**: Running asynchronously on `http://127.0.0.1:8000` (FastAPI + LangChain).
- **Web Frontend**: Running on `http://localhost:5173` (React JSX + Vite).
- **Streaming Engine**: Token-by-token real-time streaming via Server-Sent Events (SSE).
- **Centralized Security**: API keys are securely managed backend-side via `.env`. End-users do not need to enter API keys in the browser.

---

## 🤖 Supported Providers & Model Suite

| Provider Tab | Model Name | Model ID | Status | Ideal For |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini** | **Gemini Flash (Latest)** ⭐ | `gemini-flash-latest` | **ACTIVE** ✅ | Ultra-fast multimodal chat & general queries |
| **Google Gemini** | **Gemini 2.5 Flash** | `gemini-2.5-flash` | **ACTIVE** ✅ | Next-gen flash performance |
| **Google Gemini** | **Gemini 3.6 Flash** | `gemini-3.6-flash` | **ACTIVE** ✅ | State-of-the-art fast reasoning |
| **Google Gemini** | **Gemini Pro (Latest)** | `gemini-pro-latest` | **ACTIVE** ✅ | Complex analytical & long-form writing |
| **Open Models (Groq)** | **Meta Llama 3.3 (70B)** ⭐ | `llama-3.3-70b-versatile` | **ACTIVE** ✅ | Flagship 70B open-weights model |
| **Open Models (Groq)** | **DeepSeek R1 (70B)** ⭐ | `deepseek-r1-distill-llama-70b` | **ACTIVE** ✅ | Open-source reasoning, math & logic |
| **Open Models (Groq)** | **Qwen 2.5 (32B)** | `qwen-2.5-32b` | **ACTIVE** ✅ | Alibaba Cloud open model for code & math |
| **Open Models (Groq)** | **Mixtral 8x7B** | `mixtral-8x7b-32768` | **ACTIVE** 

---

## 🏗️ Architecture & Project Directory

```
langChain-chat/
├── backend/
│   ├── main.py              # FastAPI server & route registration
│   ├── config.py            # Centralized settings & modular DB/Auth placeholders
│   ├── schemas.py           # Pydantic data schemas for chat & providers
│   ├── llm_helper.py        # LangChain manager for Gemini, Groq
│   ├── requirements.txt     # Python backend dependencies
│   └── routers/
│       ├── models.py        # GET /api/models/providers metadata endpoint
│       ├── chat.py          # POST /api/chat/stream SSE token streaming endpoint
│       └── auth.py          # Modular OAuth & JWT authentication placeholder
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx        # Top bar with active model badge & OAuth button
│   │   │   ├── Sidebar.jsx       # Provider picker pills (Gemini, Open Models ), parameters & model selector
│   │   │   ├── ChatWindow.jsx    # Conversation view with empty state suggestions
│   │   │   ├── MessageBubble.jsx # Formatted message bubbles with copy-to-clipboard & error banners
│   │   │   └── ChatInput.jsx     # Autosizing text area & stop streaming button
│   │   ├── hooks/
│   │   │   └── useChat.js        # React hook managing SSE stream & conversation state
│   │   ├── services/
│   │   │   └── api.js            # Modular API client layer (SSE streaming + Auth headers)
│   │   ├── App.jsx               # Main React JSX application component
│   │   ├── main.jsx              # React DOM entry point
│   │   └── index.css             # Glassmorphism dark theme CSS system
│   ├── package.json
│   └── vite.config.js            # Vite dev server configuration with API proxying
├── .env                          # Server API keys configuration
├── .env.example                  # Environment key configuration template
└── README.md                     # Project documentation
```

---

## 🚀 Quickstart & How to Run

### 1. Configure API Keys in `.env`
Edit the `.env` file in the project root folder:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

```

### 2. Start the Backend (FastAPI + LangChain)
```bash
cd langChain-chat

# Install dependencies (if not already installed)
pip install -r backend/requirements.txt

# Start server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at `http://127.0.0.1:8000/docs`.

### 3. Start the Web Frontend (React JSX + Vite)
```bash
cd langChain-chat/frontend

# Run development server
cmd /c npm run dev
```

Open your browser at **`http://localhost:5173`**.

---

## 🔧 Technical Upgrades Made

1. **Groq Integration for Free Open-Source Models**:
   - Added `langchain-groq` integration allowing 100% free access to **Meta Llama 3.3 (70B)**, **DeepSeek R1 (70B)**, **Qwen 2.5 (32B)**, and **Mixtral 8x7B**.
2. **Robust Token Block Parsing**:
   - Resolved streaming token block structures in `backend/llm_helper.py` and `frontend/src/services/api.js` to ensure clean text output without `[object Object]` glitches.
3. **Zero-Configuration UI**:
   - Removed client-side API key prompts so users enjoy a seamless chat experience powered by system `.env` keys.
4. **Modular Architecture for Future Expansion**:
   - **Database Ready**: Prepared with SQLAlchemy/Tortoise ORM schemas in `backend/schemas.py`.
   - **OAuth Ready**: Includes `backend/routers/auth.py` router and `frontend/src/services/api.js` bearer header hooks ready for Google/GitHub OAuth and JWT session management.
