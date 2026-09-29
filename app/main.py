import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine, Base
from app.routes import clients, affaires, echeances, dashboard, documents

# Création des tables
Base.metadata.create_all(bind=engine)

# Dossier d'upload
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="Agent-Justice",
    description="Logiciel de gestion de dossiers juridiques",
    version="1.0.0"
)

# Montage des fichiers statiques
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Inclusion des routes
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(affaires.router, prefix="/api/affaires", tags=["Affaires"])
app.include_router(echeances.router, prefix="/api/echeances", tags=["Échéances"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Tableau de bord"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api")
async def api_info():
    return {"message": "Bienvenue sur Agent-Justice", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
