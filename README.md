# Chatbot Dashboard

## 1. Overview
This project is an advanced **AI-Powered Analytics Dashboard** that bridges the gap between natural language and database insights. Users can ask questions in plain English (e.g., "Show me total sales by category"), and the system autonomously translates these into SQL, executes them against a business database, and renders professional-grade visualizations (Charts) in real-time.

It features a **FastAPI** backend for robust orchestration, **Google Gemini (LLM)** for intelligent query generation, and a reactive **Vue.js** frontend for a seamless user experience.

---

## 2. Server-Side File Breakdown & Logic

The codebase is architecturally divided into three logical servers/layers. Here is the one-liner logic for each critical file:

### 🟢 Frontend Server (Client Layer)
*Responsible for UI rendering, state management, and user interaction.*

| File Path | One-Liner Logic |
|-----------|-----------------|
| `frontend/src/App.vue` | Main application shell managing global state, layout, and API base URL configuration. |
| `frontend/src/components/ChatWindow.vue` | Handles the chat interface, renders message history, and displays returned chart images. |
| `frontend/src/components/FloatingButton.vue` | A UI utility providing a floating toggle button to open/close the dashboard widget. |
| `frontend/src/services/api.js` | The generic HTTP client wrapper (Axios) responsible for all communication with the Backend API. |
| `frontend/src/main.js` | The entry point that initializes the Vue application and mounts it to the DOM. |
| `frontend/vite.config.js` | Configuration for the Vite build tool, handling local server ports and proxy settings. |

### 🔵 Backend Server (Orchestration Layer)
*Responsible for API routing, database management, and execution flow.*

| File Path | One-Liner Logic |
|-----------|-----------------|
| `backend/app/main.py` | The FastAPI application entry point; initializes the server, CORS policies, and static file mounting. |
| `backend/app/api/v1/endpoints.py` | Defines the REST API routes (`/analyze`, `/execute`) to receive client requests and delegate tasks. |
| `backend/app/core/db.py` | Manages the database connection pool and provides session generators for MySQL access. |
| `backend/app/schemas/query.py` | Defines strict Pydantic data models to validate incoming API requests and structure JSON responses. |
| `backend/app/services/query_exec.py` | Safely executes parameterized SQL queries against the database and converts results into Pandas DataFrames. |
| `backend/app/services/viz_engine.py` | Uses Matplotlib/Seaborn to generate static chart images (PNG) from dataframes based on visualization specs. |

### 🟣 Modeling Server (AI & Intelligence Layer)
*Responsible for heavy cognitive tasks, natural language understanding, and decision making.*

| File Path | One-Liner Logic |
|-----------|-----------------|
| `backend/app/services/llm_engine.py` | Interfaces with Google Gemini to translate natural language prompts into executable SQL and Visualization Specifications. |

---

## 3. Project File Structure

```text
Chatbot-Dashboard/
├── backend/                  # Backend Server Code
│   ├── app/
│   │   ├── api/v1/
│   │   │   └── endpoints.py  # API Routes
│   │   ├── core/
│   │   │   └── db.py         # DB Operations
│   │   ├── schemas/
│   │   │   └── query.py      # Data Models
│   │   ├── services/
│   │   │   ├── llm_engine.py # AI Logic (Modeling Server)
│   │   │   ├── query_exec.py # SQL Execution
│   │   │   └── viz_engine.py # Chart Rendering
│   │   └── main.py           # App Entry Point
│   ├── static/               # Generated Charts Storage
│   └── requirements.txt
├── frontend/                 # Frontend Server Code
│   ├── src/
│   │   ├── components/       # Vue Components
│   │   ├── services/         # API Integration
│   │   ├── App.vue           # Main Component
│   │   └── main.js           # Entry Point
│   └── package.json
└── README.md
```

---

### Process Flow Diagram

```mermaid
graph TD
    %% Styling - Enforcing Black Text
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000000;
    classDef backend fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000000;
    classDef external fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000000;
    classDef storage fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000000;
    classDef default color:#000000;
    
    %% Force Edge Labels to be Black
    linkStyle default color:#000000;

    User([👤 User])

    subgraph "Frontend (Vue.js)"
        UI[Chat Interface<br>ChatWindow.vue]:::frontend
        API_Client[API Service<br>api.js]:::frontend
    end

    subgraph "Backend (FastAPI)"
        Router[API Router<br>endpoints.py]:::backend
        Cache[(Job Cache<br>In-Memory Dict)]:::backend
        
        subgraph "Services"
            LLM_Service[LLM Engine<br>Prompt Engineering]:::backend
            SQL_Exec[SQL Executor<br>query_exec.py]:::backend
            Viz_Engine[Visualization Engine<br>viz_engine.py]:::backend
        end
    end

    subgraph "External & Persistence"
        Gemini[Google Gemini API]:::external
        MySQL[(MySQL Database)]:::storage
        FileStore[Static Charts<br>/static/charts]:::storage
    end

    %% Phase 1: Analysis Flow
    User -->|"1. Type Query"| UI
    UI -->|"2. POST /analyze"| Router
    Router -->|"3. Get Schema"| MySQL
    Router -->|"4. Send Prompt + Schema"| LLM_Service
    LLM_Service -->|"5. Request Translation"| Gemini
    Gemini -->|"6. Return JSON (SQL + VizSpec)"| LLM_Service
    LLM_Service --> Router
    Router -->|"7. Execute Preview (Limit 5)"| SQL_Exec
    SQL_Exec -->|"8. Fetch Rows"| MySQL
    Router -->|"9. Store Context"| Cache
    Router -->|"10. Return Preview"| UI

    %% Phase 2: Execution Flow
    User -->|"11. Click 'Execute'"| UI
    UI -->|"12. POST /execute (Job ID)"| Router
    Router -->|"13. Retrieve Context"| Cache
    Router -->|"14. Fetch Full Data (Pandas)"| SQL_Exec
    SQL_Exec -->|"15. Query Data"| MySQL
    SQL_Exec -->|"16. Return DataFrame"| Viz_Engine
    Viz_Engine -->|"17. Render Chart"| Viz_Engine
    Viz_Engine -->|"18. Save PNG"| FileStore
    Viz_Engine -->|"19. Return URL"| Router
    Router -->|"20. Display Chart"| UI
```

---

### Sequence Diagram
```mermaid
graph TD
    %% Define a standard class for black text
    classDef standard fill:#ffffff,stroke:#333333,stroke-width:2px,color:#000000;

    %% Nodes with the standard class applied
    User([User]):::standard

    subgraph "Frontend (Vue.js)"
        UI[Chat Interface<br>ChatWindow.vue]:::standard
        API_Client[API Service<br>api.js]:::standard
    end

    subgraph "Backend (FastAPI)"
        Router[API Router<br>endpoints.py]:::standard
        Cache[(Job Cache<br>In-Memory Dict)]:::standard
        
        subgraph "Services"
            LLM_Service[LLM Engine<br>Prompt Engineering]:::standard
            SQL_Exec[SQL Executor<br>query_exec.py]:::standard
            Viz_Engine[Visualization Engine<br>viz_engine.py]:::standard
        end
    end

    subgraph "External & Persistence"
        Gemini[Google Gemini API]:::standard
        MySQL[(MySQL Database)]:::standard
        FileStore[Static Charts<br>/static/charts]:::standard
    end

    %% Edge Connections
    User -->|"1. Type Query"| UI
    UI -->|"2. POST /analyze"| Router
    Router -->|"3. Get Schema"| MySQL
    Router -->|"4. Send Prompt + Schema"| LLM_Service
    LLM_Service -->|"5. Request Translation"| Gemini
    Gemini -->|"6. Return JSON (SQL + VizSpec)"| LLM_Service
    LLM_Service --> Router
    Router -->|"7. Execute Preview (Limit 5)"| SQL_Exec
    SQL_Exec -->|"8. Fetch Rows"| MySQL
    Router -->|"9. Store Context"| Cache
    Router -->|"10. Return Preview"| UI

    %% Phase 2 Execution
    User -->|"11. Click Execute"| UI
    UI -->|"12. POST /execute (Job ID)"| Router
    Router -->|"13. Retrieve Context"| Cache
    Router -->|"14. Fetch Full Data (Pandas)"| SQL_Exec
    SQL_Exec -->|"15. Query Data"| MySQL
    SQL_Exec -->|"16. Return DataFrame"| Viz_Engine
    Viz_Engine -->|"17. Render Chart"| Viz_Engine
    Viz_Engine -->|"18. Save PNG"| FileStore
    Viz_Engine -->|"19. Return URL"| Router
    Router -->|"20. Display Chart"| UI
```

--- 

## 4. Setup & Installation

### Prerequisites
*   **Python 3.9+**
*   **Node.js 16+** & **npm**
*   **MySQL Database** (via XAMPP or Docker)

### Step 1: Database Configuration
1.  Ensure MySQL is running.
2.  Create a database named `analytics_db`.
3.  Populate it with your data (e.g., a `sales` table).
4.  Update `DATABASE_URL` in `backend/app/core/db.py` if needed.

### Step 2: Backend Setup
```bash
cd backend
# Install Python dependencies
pip install -r requirements.txt

# Create .env file with your Gemini API Key
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Start the Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*The Backend will be live at `http://localhost:8000`*

### Step 3: Frontend Setup
```bash
cd frontend
# Install Node dependencies
npm install

# Start the Development Server
npm run dev
```
*The Frontend will be live at `http://localhost:5173`*

---

## 5. API Integration & Requests

The system uses a **2-Phase Execution Model** to ensure accuracy.

### Phase 1: Analysis (Natural Language -> SQL)
**Endpoint**: `POST /api/v1/analyze`

*   **Logic**: The Modeling Server translates the prompt into SQL and a Visualization Spec. It returns a "preview" (first 5 rows) for user verification.
*   **Request**:
    ```json
    {
      "prompt": "Show me total revenue by product category",
      "context_tables": ["sales_data"]
    }
    ```
*   **Response**: Returns `job_id`, `generated_sql`, `viz_spec`, and `preview_rows`.

### Phase 2: Execution (SQL -> Chart)
**Endpoint**: `POST /api/v1/execute`

*   **Logic**: The Backend executes the full query (cached by `job_id`), generates the chart image, and returns the URL.
*   **Request**:
    ```json
    {
      "job_id": "unique-job-uuid-123"
    }
    ```
*   **Response**:
    ```json
    {
      "status": "completed",
      "chart_url": "/static/charts/chart_uuid.png",
      "data_summary": { "total_rows": 150 }
    }
    ```
