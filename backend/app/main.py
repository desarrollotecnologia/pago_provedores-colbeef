from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from app.api.routes import auth, catalogos, lotes, proveedores, sistema, usability
from app.core.config import get_settings
from app.core.database import engine
from app.models import CambioProveedor, EventoUsabilidad
from app.version import APP_VERSION, EMAIL_TEMPLATE_VERSION

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Sistema de gestión de pagos a proveedores",
    version=APP_VERSION,
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
app.include_router(usability.router, prefix=API_PREFIX)


@app.on_event("startup")
def ensure_usability_table() -> None:
    """Garantiza tablas auxiliares en instalaciones que no corrieron migrate."""
    EventoUsabilidad.__table__.create(bind=engine, checkfirst=True)
    CambioProveedor.__table__.create(bind=engine, checkfirst=True)


@app.on_event("startup")
def sync_tipos_identificacion() -> None:
    """Sincroniza el catálogo y calcula el DV de los NIT existentes."""
    from sqlalchemy import select

    from app.core.database import SessionLocal
    from app.core.nit import (
        TIPOS_IDENTIFICACION_NIT,
        calcular_digito_verificacion_nit,
    )
    from app.models import Proveedor, TipoIdentificacion
    from app.seeds.seed_catalogos import TIPOS_IDENTIFICACION

    db = SessionLocal()
    try:
        for codigo, descripcion in TIPOS_IDENTIFICACION:
            tipo = db.get(TipoIdentificacion, codigo)
            if tipo is None:
                db.add(TipoIdentificacion(codigo=codigo, descripcion=descripcion))
            elif tipo.descripcion != descripcion:
                tipo.descripcion = descripcion

        for proveedor in db.scalars(select(Proveedor)):
            if proveedor.tipo_identificacion in TIPOS_IDENTIFICACION_NIT:
                try:
                    proveedor.digito_verificacion = calcular_digito_verificacion_nit(
                        proveedor.identificacion
                    )
                except ValueError:
                    pass
            else:
                proveedor.digito_verificacion = 0
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"[startup] No se pudo sincronizar tipos de identificación: {exc}")
    finally:
        db.close()


@app.on_event("startup")
def repair_lote_totals_on_startup() -> None:
    """Corrige importe_total desactualizado en lotes existentes."""
    from app.core.database import SessionLocal
    from app.services import lote_service

    db = SessionLocal()
    try:
        n = lote_service.reparar_totales_lotes(db)
        db.commit()
        if n:
            print(f"[startup] Totales de {n} lote(s) sincronizados")
    except Exception as exc:
        db.rollback()
        print(f"[startup] No se pudieron reparar totales de lotes: {exc}")
    finally:
        db.close()


@app.get("/health")
def health_check():
    routes = {getattr(r, "path", "") for r in app.routes}
    historial_ok = "/api/historial/pagos" in routes or "/api/lotes/historial/pagos" in routes
    return {
        "status": "ok",
        "version": APP_VERSION,
        "email_template": EMAIL_TEMPLATE_VERSION,
        "env": settings.app_env,
        "app_url": settings.app_url,
        "historial": historial_ok,
    }


# Frontend estático — misma URL que la API (sin configurar rutas al migrar)
static_dir = settings.static_dir

_NO_CACHE = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}


class NoCacheStaticFiles(StaticFiles):
    """Evita que el navegador sirva JS/CSS viejos tras un deploy."""

    async def get_response(self, path: str, scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers.update(_NO_CACHE)
        return response


if (static_dir / "assets").exists():
    app.mount(
        "/assets",
        NoCacheStaticFiles(directory=static_dir / "assets"),
        name="assets",
    )


def _spa_index():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(index, headers=_NO_CACHE)
    return {
        "message": "API activa. Frontend no encontrado en frontend/dist",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/email-banner-colbeef.png")
def email_banner():
    from app.services.email_assets import get_banner_path

    path = get_banner_path()
    if not path:
        raise HTTPException(status_code=404, detail="Banner de correo no instalado")
    return FileResponse(path, media_type="image/png")


@app.get("/colbeef-logo.png")
def colbeef_logo():
    """Logo del login — también servido vía /assets tras el build de Vite."""
    candidates = [
        static_dir / "colbeef-logo.png",
        settings.project_root / "frontend" / "public" / "colbeef-logo.png",
        settings.project_root / "frontend" / "src" / "assets" / "colbeef-logo.png",
    ]
    for path in candidates:
        if path.is_file():
            return FileResponse(path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo Colbeef no encontrado")


@app.get("/")
def spa_index():
    return _spa_index()


@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    """Rutas del SPA (React Router) — devuelve index.html."""
    if full_path.startswith("api") or full_path in ("docs", "openapi.json", "health", "redoc"):
        raise HTTPException(status_code=404)
    if full_path.startswith("assets/") or full_path in (
        "email-banner-colbeef.png",
        "colbeef-logo.png",
    ):
        raise HTTPException(status_code=404)
    return _spa_index()
