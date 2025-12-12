from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 

from app.api.v1 import endpoints # Import the router

# 1. Initialize the application
app = FastAPI(title="DataChat API", version="v1")

# 2. CORS Configuration for Frontend Integration (localhost:5173 is Vue dev server)
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Mount Static Files for serving generated charts
# The 'static' directory holds the final PNGs.
app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. Include API Endpoints
app.include_router(endpoints.router, prefix="/api/v1")


@app.get("/health")
def read_root():
    """Simple health check endpoint."""
    return {"status": "ok"}