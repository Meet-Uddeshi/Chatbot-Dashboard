## Features

- **Natural Language Processing**: Convert user questions into SQL queries.
- **Dynamic Visualization**: Automatically generates Bar, Line, or Pie charts based on data.
- **Interactive Chat Interface**: A clean Vue.js based chat widget.
- **RESTful API**: FastAPI backend for robust data handling.

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.x
- **Database Helper**: SQLAlchemy, PyMySQL
- **Data Analysis**: Pandas
- **Visualization Logic**: Matplotlib, Seaborn

### Frontend
- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **HTTP Client**: Axios

### Database
- **System**: MySQL (via XAMPP)

## Project Structure

```
Chatbot-Dashboard/
├── backend/
│   ├── app/
│   │   ├── api/                 # Route handlers
│   │   │   └── v1/
│   │   │       └── endpoints.py
│   │   ├── core/
│   │   │   └── db.py            # Database connection logic
│   │   ├── schemas/             # Pydantic models
│   │   ├── services/
│   │   │   └── query_exec.py    # SQL execution logic
│   │   ├── __init__.py
│   │   └── main.py              # FastAPI entry point
│   ├── static/                  # Local storage for generated charts
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── chat-widget-loader.js # Embed script for 3rd party sites
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChartDisplay.vue
│   │   │   ├── ChatWindow.vue
│   │   │   └── FloatingButton.vue
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── data/                        # Database initialization/data
├── n8n/                         # Workflow automation
│   └── workflows/
├── .env.example
└── docker-compose.yml
```

## Setup & Installation

### Prerequisites
- Python 3.9+ installed
- Node.js & npm installed
- XAMPP installed (for MySQL database)

### 1. Database Setup
1. Start **XAMPP** and ensure the **MySQL** and **Apache** module is running.
2. Create a database named `analytics_db` (or update `DATABASE_URL` in `backend/app/core/db.py`).
3. Ensure your MySQL user is `root` with no password, or update the connection settings accordingly.

### 2. Backend Setup
Navigate to the backend directory:
```bash
cd backend
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Frontend Setup
Navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

## Running the Application

### 1. Start the Backend Server
From the `backend` directory:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`.

### 2. Start the Frontend Client
From the `frontend` directory:
```bash
npm run dev
```
The application will typically run at `http://localhost:5173`.

## API Usage

### Endpoint: `/api/v1/analyze`

**Method**: `POST`

**Request**:
```json
{
  "prompt": "Show me total sales by category",
  "context_tables": ["sales"]
}
```

**Response**:
```json
{
  "job_id": "e4369be5-2c64-48a3-9f2c-df5e90c6ab64",
  "generated_sql": "SELECT category, SUM(amount) AS total_sales FROM sales GROUP BY category...",
  "viz_spec": { 
      "type": "bar",
      "x": "category",
      "y": "total_sales",
      "title": "Total Sales by Category"
  },
  "preview_rows": [
      { "category": "Electronics", "total_sales": "650.00" }
  ]
}
```
