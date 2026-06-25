"""Recursos estáticos para correos (banner Colbeef, etc.)."""
from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings

BANNER_FILENAME = "email-banner-colbeef.png"
BANNER_ORIGINAL_FILENAME = "FIRMAS COLBEEF_Mesa de trabajo 1 (1).png"
BANNER_CID = "colbeef_banner"


def banner_candidates() -> list[Path]:
    s = get_settings()
    return [
        s.project_root / "backend" / "app" / "static" / BANNER_FILENAME,
        s.project_root / "frontend" / "public" / BANNER_FILENAME,
        s.project_root / "frontend" / "public" / BANNER_ORIGINAL_FILENAME,
        s.static_dir / BANNER_FILENAME,
        s.static_dir / BANNER_ORIGINAL_FILENAME,
    ]


def get_banner_path() -> Path | None:
    custom = get_settings().email_firma_banner_path
    if custom:
        p = Path(custom)
        if p.is_file():
            return p
    for p in banner_candidates():
        if p.is_file():
            return p
    return None


def banner_public_url() -> str | None:
    """URL pública del banner (vista previa / fallback HTML)."""
    s = get_settings()
    if s.email_firma_banner_url:
        return s.email_firma_banner_url
    if get_banner_path():
        return f"{s.app_url.rstrip('/')}/{BANNER_FILENAME}"
    return None
