"""
Chemistry Web App — FastAPI Backend
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.routes import elements, compounds, reactions

app = FastAPI(
    title="Chemistry App API",
    description="Periodni sistem i kombinovanje jedinjenja",
    version="1.0.0",
)

# CORS — allow frontend dev server
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=CORS_ORIGINS,
    allow_origins=["*"],  # Dozvoljava Vercel-u i bilo kom drugom sajtu da povuče podatke
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(elements.router, prefix="/elements", tags=["elements"])
app.include_router(compounds.router, prefix="/compounds", tags=["compounds"])
app.include_router(reactions.router, prefix="/reactions", tags=["reactions"])


@app.get("/")
def root():
    return {"status": "ok", "app": "Chemistry API"}

