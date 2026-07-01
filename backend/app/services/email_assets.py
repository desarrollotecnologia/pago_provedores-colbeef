"""Recursos estáticos para correos (banner Colbeef, iconos de firma, etc.)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings

BANNER_FILENAME = "email-banner-colbeef.png"
BANNER_ORIGINAL_FILENAME = "FIRMAS COLBEEF_Mesa de trabajo 1 (1).png"
BANNER_CID = "colbeef_banner"
LOGO_FILENAME = "colbeef-logo.png"
LOGO_CID = "colbeef_logo"
ICONS_DIRNAME = "email-icons"


@dataclass(frozen=True)
class EmailIcon:
    cid: str
    filename: str


ICON_PHONE = EmailIcon("colbeef_icon_phone", "icon-phone.png")
ICON_EMAIL = EmailIcon("colbeef_icon_email", "icon-email.png")
ICON_LOCATION = EmailIcon("colbeef_icon_location", "icon-location.png")
ICON_WEB = EmailIcon("colbeef_icon_web", "icon-web.png")
ICON_FACEBOOK = EmailIcon("colbeef_icon_facebook", "icon-facebook.png")
ICON_LINKEDIN = EmailIcon("colbeef_icon_linkedin", "icon-linkedin.png")
ICON_X = EmailIcon("colbeef_icon_x", "icon-x.png")
ICON_INSTAGRAM = EmailIcon("colbeef_icon_instagram", "icon-instagram.png")

SIGNATURE_ICONS: tuple[EmailIcon, ...] = (
    ICON_PHONE,
    ICON_EMAIL,
    ICON_LOCATION,
    ICON_WEB,
    ICON_FACEBOOK,
    ICON_LINKEDIN,
    ICON_X,
    ICON_INSTAGRAM,
)


def icon_candidates(icon: EmailIcon) -> list[Path]:
    s = get_settings()
    return [
        s.project_root / "backend" / "app" / "static" / ICONS_DIRNAME / icon.filename,
        s.static_dir / ICONS_DIRNAME / icon.filename,
    ]


def icons_dir() -> Path:
    for icon in SIGNATURE_ICONS:
        path = get_icon_path(icon)
        if path:
            return path.parent
    s = get_settings()
    return s.project_root / "backend" / "app" / "static" / ICONS_DIRNAME


def get_icon_path(icon: EmailIcon) -> Path | None:
    for path in icon_candidates(icon):
        if path.is_file():
            return path
    return None


def logo_candidates() -> list[Path]:
    s = get_settings()
    return [
        s.project_root / "backend" / "app" / "static" / LOGO_FILENAME,
        s.project_root / "frontend" / "public" / LOGO_FILENAME,
        s.project_root / "frontend" / "src" / "assets" / LOGO_FILENAME,
        s.static_dir / LOGO_FILENAME,
    ]


def get_logo_path() -> Path | None:
    for path in logo_candidates():
        if path.is_file():
            return path
    return None


def inline_attachments() -> list[tuple[str, Path]]:
    """Recursos embebidos como cid: (Content-ID, ruta en disco)."""
    items: list[tuple[str, Path]] = []
    logo = get_logo_path()
    if logo:
        items.append((LOGO_CID, logo))
    banner = get_banner_path()
    if banner and not get_settings().email_firma_banner_url:
        items.append((BANNER_CID, banner))
    for icon in SIGNATURE_ICONS:
        path = get_icon_path(icon)
        if path:
            items.append((icon.cid, path))
    return items


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
