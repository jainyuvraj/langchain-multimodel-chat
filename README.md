# ⚡ PolyModel AI - Multi-Model Vector Chatbot Platform

A production-grade, highly modular multi-model AI chatbot platform built using **Python (FastAPI + LangChain)** and **React (JSX) + Vite** in a single unified monorepo.

Featuring **Google OAuth2 Authentication**, **ChromaDB Semantic Vector Memory**, **SQLite Database Thread Persistence**, and real-time token streaming across **Google Gemini**, **Groq Open Models (Llama 3.3, Qwen 3.6, GPT-OSS)**, **OpenAI**, and **Anthropic Claude**.

---

## 🌟 Current Status & Key Features

### Current Status: **LIVE & OPERATIONAL** 🟢

- **Backend API**: Running asynchronously on `http://127.0.0.1:8000` (FastAPI + LangChain + SQLAlchemy + ChromaDB).
- **Web Frontend**: Running on `http://localhost:5173` (React JSX + Vite).
- **Real-Time Streaming**: Token-by-token streaming via Server-Sent Events (SSE) with page-refresh resilience.
- **Security & Auth**: Google OAuth2 & JWT tokens. API keys managed securely on the server via `.env`.

---

## 🤖 Supported Providers & Active Models

| Provider Tab | Model Name | Model ID | Status | Ideal For |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini** | **Gemini Flash (Latest)** ⭐ | `gemini-flash-latest` | **ACTIVE** ✅ | Ultra-fast multimodal chat & general queries |
| **Google Gemini** | **Gemini 2.5 Flash** | `gemini-2.5-flash` | **ACTIVE** ✅ | Next-gen flash performance |
| **Google Gemini** | **Gemini 3.6 Flash** | `gemini-3.6-flash` | **ACTIVE** ✅ | State-of-the-art fast reasoning |
| **Google Gemini** | **Gemini Pro (Latest)** | `gemini-pro-latest` | **ACTIVE** ✅ | Complex analytical & long-form writing |
| **Open Models (Groq)** | **Meta Llama 3.3 (70B)** ⭐ | `llama-3.3-70b-versatile` | **ACTIVE** ✅ | Flagship 70B open-weights model |
| **Open Models (Groq)** | **Qwen 3.6 (27B)** ⭐ | `qwen/qwen3.6-27b` | **ACTIVE** ✅ | Alibaba Cloud open model for reasoning & code |
| **Open Models (Groq)** | **GPT-OSS (120B)** | `openai/gpt-oss-120b` | **ACTIVE** ✅ | High-capacity open model by OpenAI |
| **Open Models (Groq)** | **Llama 3.1 8B Instant** | `llama-3.1-8b-instant` | **ACTIVE** ✅ | Ultra-fast compact model |
| **OpenAI** | **GPT-4o** | `gpt-4o` | Configured | Multi-step reasoning & general knowledge |
| **OpenAI** | **GPT-4o Mini** | `gpt-4o-mini` | Configured | Fast lightweight tasks |
| **Anthropic** | **Claude 3.5 Sonnet** | `claude-3-5-sonnet-20240620` | Configured | State-of-the-art code & text analysis |

---

## 🧠 Hybrid Vector Memory & Context Architecture

The application uses a **hybrid context management engine** combining long-term semantic retrieval and short-term dialogue window:

1. **System Prompt**: Base persona instructions.
2. **Top 5 Vector Memory Matches**: ChromaDB queries message embeddings for top-5 historical turns matching the user query.
3. **Cross-Thread Memory Toggle (UI Control)**:
   - **Toggle OFF (Default)**: Searches vector memory strictly within the **current chat thread** (`chatID`).
   - **Toggle ON**: Searches vector memory across **all saved threads** under the authenticated user (`userID`).
4. **Recent 5 Messages**: Includes exact last 5 short-term turns to preserve dialogue flow.

---

## 🔒 Authentication & Chat Thread Restrictions

- **Google OAuth2 & JWT**: Sign in with Google to sync user profile (`email`, `name`, `avatar`) and issue signed JWT tokens.
- **Guest Mode Restrictions**: Unauthenticated / Guest users are limited to **1 single chat thread**.
- **Authenticated Google Users**: Unlocks **unlimited saved chat threads**, thread deletion, and cross-session vector memory sync.

---

## 🏗️ Project Directory Structure

```
langChain-chat/
├── backend/
│   ├── main.py              # FastAPI app & database table initialization
│   ├── config.py            # Settings, CORS, OAuth keys, database URLs
│   ├── db.py                # SQLAlchemy engine & session factory
│   ├── models_db.py         # SQLAlchemy ORM Models (UserDB, ChatSessionDB, ChatMessageDB)
│   ├── schemas.py           # Pydantic schemas for Auth, Chat, Sessions
│   ├── auth_service.py      # JWT issuance, token verification, guest fallback
│   ├── vector_service.py    # ChromaDB vector store manager (embeddings & search)
│   ├── llm_helper.py        # LangChain model manager & hybrid vector context builder
│   ├── requirements.txt     # Python backend dependencies
│   └── routers/
│       ├── models.py        # Provider & model metadata endpoint
│       ├── chat.py          # SSE token streaming & post-stream persistence
│       ├── auth.py          # Google OAuth callback & profile endpoints
│       └── sessions.py      # ChatSession CRUD endpoints (chatID per userID)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx                # Top bar with model badge & UserMenu
│   │   │   ├── Sidebar.jsx               # Model picker, sliders & Cross-Thread toggle
│   │   │   ├── ChatHistorySidebar.jsx    # Saved chat threads list & + New Chat button
│   │   │   ├── ChatWindow.jsx           # Chat transcript view with suggestions
│   │   │   ├── MessageBubble.jsx         # Formatted message bubbles & copy button
│   │   │   ├── ChatInput.jsx             # Autosizing input & stop button
│   │   │   ├── UserMenu.jsx              # Avatar pill & logout dropdown
│   │   │   └── AuthModal.jsx             # Login modal (Google OAuth & Guest Mode)
│   │   ├── context/
│   │   │   └── AuthContext.jsx           # React Context for JWT & user profile state
│   │   ├── hooks/
│   │   │   └── useChat.js                # Custom hook for chat state & session management
│   │   ├── services/
│   │   │   └── api.js                    # Modular API client layer (SSE stream + Bearer tokens)
│   │   ├── App.jsx                       # Main React application component
│   │   ├── main.jsx                      # React DOM entry
│   │   └── index.css                     # Glassmorphic dark theme CSS system
│   ├── package.json
│   └── vite.config.js                    # Vite dev server config with API proxying
├── .env                                  # Server API keys & OAuth secrets
├── .env.example                          # Environment configuration template
├── .gitignore                            # Excludes .env, node_modules, *.bin, *.db
└── README.md                             # Documentation
```

---

## 🚀 Quickstart & Setup Guide

### 1. Configure `.env`
Create or edit `.env` in the root project directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
```

### 2. Start the Backend Server
```bash
cd langChain-chat
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start the Web Frontend
```bash
cd langChain-chat/frontend
cmd /c npm run dev
```

Open **`http://localhost:5173`** in your browser!
