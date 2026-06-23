"""Configuración centralizada — único punto para migración entre servidores."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Raíz del proyecto (carpeta que contiene backend/, scripts/, .env)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _env_int(key: str, default: int) -> int:
    try:
        return int(_env(key, str(default)))
    except ValueError:
        return default


def _env_bool(key: str, default: bool = False) -> bool:
    return _env(key, str(default).lower()).lower() in ("1", "true", "yes", "on")


class Settings:
    """Toda la configuración del sistema. Al migrar, solo editar .env."""

    def __init__(self) -> None:
        self.project_root = PROJECT_ROOT
        self.app_env = _env("APP_ENV", "development")
        self.app_name = _env("APP_NAME", "Pago Proveedores - Colbeef")

        # Red / API
        self.api_host = _env("API_HOST", "0.0.0.0")
        self.api_port = _env_int("API_PORT", 8100)
        self.app_url = _env("APP_URL") or f"http://localhost:{self.api_port}"

        # Base de datos
        self.database_url = _env(
            "DATABASE_URL",
            "mysql+pymysql://root:@localhost:3306/pago_proveedores?charset=utf8mb4",
        )

        # Seguridad
        self.secret_key = _env("SECRET_KEY", "dev-secret-key-change-in-production")
        self.access_token_expire_minutes = _env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 480)

        # Rutas relativas al proyecto (portables)
        self.output_dir = PROJECT_ROOT / _env("OUTPUT_DIR", "output")
        self.static_dir = PROJECT_ROOT / _env("STATIC_DIR", "frontend/dist")
        self.excel_path = _env("EXCEL_PATH") or str(
            Path.home() / "Downloads" / "MODELO PAGO PROVEEDORES (1).xls"
        )

        # CORS — incluir localhost y la URL pública (IP o dominio)
        cors = _env("CORS_ORIGINS")
        port = self.api_port
        defaults = {
            self.app_url,
            f"http://localhost:{port}",
            f"http://127.0.0.1:{port}",
        }
        if cors:
            self.cors_origins = list(defaults | {o.strip() for o in cors.split(",") if o.strip()})
        else:
            self.cors_origins = list(defaults)

        # Archivo plano
        self.ciudad_default = _env("CIUDAD_DEFAULT", "BOGOTA")
        self.concepto_padding = _env_int("CONCEPTO_PADDING", 76)

        # SMTP (correos) — pueden sobreescribirse desde BD en runtime
        self.smtp_host = _env("SMTP_HOST", "")
        self.smtp_port = _env_int("SMTP_PORT", 587)
        self.smtp_user = _env("SMTP_USER", "coordinacion.tesoreria@colbeef.com")
        self.smtp_password = _env("SMTP_PASSWORD", "")
        self.smtp_from_email = _env("SMTP_FROM_EMAIL", self.smtp_user)
        self.smtp_from_name = _env("SMTP_FROM_NAME", "Coordinación Tesorería")
        self.smtp_use_tls = _env_bool("SMTP_USE_TLS", True)

        # MySQL scripts Windows (opcional)
        self.mysql_bin = _env(
            "MYSQL_BIN", r"C:\Program Files\MySQL\MySQL Server 8.4\bin"
        )
        self.mysql_data = _env(
            "MYSQL_DATA", r"C:\ProgramData\MySQL\MySQL Server 8.4\Data"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reload_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
