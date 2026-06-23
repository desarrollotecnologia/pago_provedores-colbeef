from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, catalogos, lotes, proveedores, sistema
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Sistema de gestión de pagos a proveedores",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(sistema.router, prefix=API_PREFIX)
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(proveedores.router, prefix=API_PREFIX)
app.include_router(catalogos.router, prefix=API_PREFIX)
app.include_router(lotes.router, prefix=API_PREFIX)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "env": settings.app_env,
        "app_url": settings.app_url,
    }


# Frontend estático — misma URL que la API (sin configurar rutas al migrar)
static_dir = settings.static_dir
if (static_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")


def _spa_index():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index)
    return {
        "message": "API activa. Frontend no encontrado en frontend/dist",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/")
def spa_index():
    return _spa_index()


@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    """Rutas del SPA (React Router) — devuelve index.html."""
    if full_path.startswith("api") or full_path in ("docs", "openapi.json", "health", "redoc"):
        raise HTTPException(status_code=404)
    if full_path.startswith("assets/"):
        raise HTTPException(status_code=404)
    return _spa_index()
