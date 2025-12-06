### File Structure

```
Chatbot-Dashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/                 # Route handlers
│   │   │   └── v1/
│   │   │       └── endpoints.py
│   │   ├── core/
│   │   │   ├── config.py        # Env vars (DB_URL, LLM_KEY)
│   │   │   └── security.py      # Token auth (optional for MVP)
│   │   ├── services/
│   │   │   ├── llm_engine.py    # NL -> SQL + VizSpec logic
│   │   │   ├── query_exec.py    # Safe SQL execution (SQLAlchemy)
│   │   │   └── viz_engine.py    # Matplotlib/Seaborn rendering
│   │   └── schemas/             # Pydantic models
│   │       └── query.py
│   ├── static/                  # Local storage for generated charts
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── chat-widget-loader.js # Embed script for 3rd party sites
│   ├── src/
│   │   ├── components/
│   │   │   ├── FloatingButton.vue
│   │   │   ├── ChatWindow.vue
│   │   │   └── ChartDisplay.vue
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.vue
│   ├── package.json
│   └── Dockerfile
├── data/                        # Init scripts for DB
│   └── init.sql
├── n8n/                         # Workflow automation
│   └── workflows/
├── .env.example
└── docker-compose.yml
```

---

