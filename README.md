# Chatbot Dashboard

## 1. Overview
This project is an advanced **AI-Powered Analytics Dashboard** that bridges the gap between natural language and database insights. Users can ask questions in plain English (e.g., "Show me total sales by category"), and the system autonomously translates these into SQL, executes them against a business database, and renders professional-grade visualizations (Charts) in real-time.

It features a **FastAPI** backend for robust orchestration, **Google Gemini (LLM)** for intelligent query generation, and a reactive **Vue.js** frontend for a seamless user experience.

---

## 2. System Architecture (Mermaid Diagram)

The following diagram represents the core logic flow from user input to visual output.

```mermaid
graph TD
    User[User] -->|1. Asks Question| Frontend[Frontend Server (Vue.js)]
    Frontend -->|2. POST /analyze| Backend[Backend Server (FastAPI)]
    
    subgraph "Backend Orchestration"
    Backend -->|3. Get Schema Context| DB[(MySQL Database)]
    Backend -->|4. Send Prompt + Schema| Model[Modeling Server (Gemini)]
    Model -->|5. Return SQL + Viz Spec| Backend
    end
    
    Backend -->|6. JSON Preview| Frontend
    User -->|7. Confirms Action| Frontend
    Frontend -->|8. POST /execute| Backend
    
    subgraph "Execution & Rendering"
    Backend -->|9. Run SQL| DB
    DB -->|10. Raw Data| Backend
    Backend -->|11. Render Image| Viz[Viz Engine]
    Viz -->|12. Save Chart (.png)| Static[Static Files]
    end
    
    Backend -->|13. Return Chart URL| Frontend
    Frontend -->|14. Render Chart| User
```

---

## 3. Server-Side File Breakdown & Logic

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

## 4. Project File Structure

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

## 5. Setup & Installation

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

## 6. API Integration & Requests

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
