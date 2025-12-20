import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="DataChat API", version="v1")

os.makedirs("static/charts", exist_ok=True)

from app.api.v1 import endpoints 

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

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/health")
def read_root():
    return {"status": "ok"}