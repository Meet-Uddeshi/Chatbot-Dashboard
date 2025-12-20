# Chatbot Dashboard

## Overview
This project is a sophisticated **Chatbot Dashboard** that allows users to query their database using natural language. It leverages a **FastAPI** backend to handle requests, integrates with **Google Gemini (LLM)** to translate questions into SQL queries, and uses **Vue.js** for an interactive frontend. The system can execute these queries against a **MySQL** database and generate dynamic visualizations (charts) using **Matplotlib/Seaborn**, which are then displayed to the user.

## System Architecture

The following diagram illustrates the data flow within the application:

```mermaid
graph TD
    User[User] -->|1. Asks Question| Frontend[Frontend (Vue.js)]
    Frontend -->|2. POST /analyze| Backend[Backend (FastAPI)]
    
    subgraph "Backend Processing"
    Backend -->|3. Schema & Prompt| LLM[LLM Engine (Gemini)]
    LLM -->|4. SQL & Viz Spec| Backend
    end
    
    Backend -->|5. Preview JSON| Frontend
    User -->|6. Confirms Execution| Frontend
    Frontend -->|7. POST /execute| Backend
    
    subgraph "Data & Visualization"
    Backend -->|8. Execute SQL| DB[(MySQL Database)]
    DB -->|9. Raw Data| Backend
    Backend -->|10. Dataframe| Viz[Viz Engine (Matplotlib)]
    Viz -->|11. Chart Image| FS[File System (/static)]
    end
    
    Backend -->|12. Chart URL| Frontend
    Frontend -->|13. Display Chart| User
```

## Server-Side Breakdown

To better understand the deployment logic, the files are categorized by which "Server" or logical node they belong to:

### 1. Frontend Server (UI & Client Layer)
*Served via Nginx / Apache / Vite*
- **`frontend/src/App.vue`**: The main application shell managing global state (chat visibility, API URL).
- **`frontend/src/components/ChatWindow.vue`**: Handles the chat UI logic, message rendering, and user input.
- **`frontend/src/components/FloatingButton.vue`**: A lightweight visual component for toggling the dashboard.
- **`src/services/api.js`**: The communication bridge; handles all Axios HTTP requests to the Backend Server.
- **`src/main.js`**: The client-side entry point that hydrates the Vue application.

### 2. Backend Server (API & Orchestration)
*Running on FastAPI (Python/Uvicorn)*
- **`backend/app/main.py`**: The central application hub; initializes the API, CORS settings, and static file serving.
- **`app/api/v1/endpoints.py`**: The traffic controller; receives frontend requests (`/analyze`, `/execute`) and routes them to specific services.
- **`app/core/db.py`**: The database persistence layer; manages connection pooling to the MySQL database.
- **`app/schemas/query.py`**: The data contract layer; defines strict Pydantic models to validate incoming JSON and outgoing responses.
- **`app/services/query_exec.py`**: The execution engine; runs the actual SQL queries against the database and formats results.
- **`app/services/viz_engine.py`**: The rendering engine; processes dataframes to generate static chart images (CPU-intensive).

### 3. Modeling Server (AI & High-Compute)
*Logic often delegated to GPU instances or External APIs (Google Gemini)*
- **`backend/app/services/llm_engine.py`**: **The Brain**. This module interacts with high-performance LLMs (Gemini Pro/Flash). It encapsulates the complex prompt engineering and schema context injection required to translate English into accurate SQL. In a scaled architecture, this would potentially run as a separate microservice on a GPU-optimized server.

## Features
- **Natural Language to SQL**: Converts English questions into complex SQL queries automatically.
- **Dynamic Visualization**: Autonomously determines the best chart type (Bar, Line, Scatter, Heatmap) for the data.
- **Review & Execute**: distinct two-phase process (Analyze -> Execute) allowing users to verify the SQL before running it.
- **Interactive UI**: A clean, modern chat interface built with Vue 3.

## Tech Stack
- **Backend**: FastAPI, Python 3.9+, SQLAlchemy, Pandas, Matplotlib, Seaborn.
- **Frontend**: Vue 3, Vite, Axios.
- **AI/LLM**: Google Gemini (via `google-generativeai` SDK).
- **Database**: MySQL.

## Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js & npm
- MySQL (XAMPP recommended)

### 1. Database Setup
1. Start MySQL.
2. Create a database named `analytics_db`.
3. Ensure `sales_data` or relevant tables exist.
4. Update `DATABASE_URL` in `backend/app/core/db.py` if your credentials differ from `root` (no password).

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*Server runs at `http://localhost:8000`*

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
*Client runs at `http://localhost:5173`*

## API Usage

**POST** `/api/v1/analyze`
- **Input**: `{"prompt": "Show sales by category", "context_tables": ["sales_data"]}`
- **Output**: JSON with `job_id`, `generated_sql`, and `viz_spec`.

**POST** `/api/v1/execute`
- **Input**: `{"job_id": "..."}`
- **Output**: JSON with `chart_url` pointing to the generated image.

