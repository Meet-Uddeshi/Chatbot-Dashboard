### File Structure

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

---

