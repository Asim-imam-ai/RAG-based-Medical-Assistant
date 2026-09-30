# 💻 Medical Assistant - Streamlit Frontend

This directory contains the user interface for the **Healthcare RBAC RAG Medical Assistant**, built with [Streamlit](https://streamlit.io/).

---

## 🚀 Quick Start

### 1. Configure Environment
Copy `.env.example` to `.env` and set the backend API URL:

```bash
cp .env.example .env
```

Ensure `API_URL` points to your active FastAPI backend:
```env
API_URL=http://127.0.0.1:8000
```

### 2. Run the Frontend

From the root project directory:
```bash
streamlit run frontend/main.py
```

Or from inside the `frontend/` directory:
```bash
streamlit run main.py
```

---

## 🌟 Features

- **Authentication Tabs**: Secure user signup and login with role selection (`admin`, `doctor`, `nurse`, `patient`, `other`).
- **Dynamic Role UI**:
  - **Admin**: Document ingestion control with target role classification.
  - **All Roles**: Interactive clinical question-answering interface with citation inspection expanders.
- **Session Persistence**: Maintains authentication state across page interactions using Streamlit's `session_state`.
