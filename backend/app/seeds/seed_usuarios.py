"""Usuarios preconfigurados para pruebas."""
from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import Usuario

USUARIOS_INICIALES = [
    {
        "username": "viviana",
        "nombre_completo": "VIVIANA ANDREA",
        "password": "Colbeef2026*",
        "rol": "admin",
    },
    {
        "username": "panel",
        "nombre_completo": "Panel",
        "password": "123456789",
        "rol": "operador",
    },
]


def _normalizar_nombre(nombre: str) -> str:
    return nombre.strip().lower()


def seed_usuarios() -> None:
    db = SessionLocal()
    try:
        for data in USUARIOS_INICIALES:
            nombre_norm = _normalizar_nombre(data["nombre_completo"])
            exists = db.scalar(
                select(Usuario).where(
                    func.lower(Usuario.username) == data["username"].lower()
                )
            )
            if exists:
                print(f"  Usuario '{data['username']}' ya existe, omitido.")
                continue

            db.add(
                Usuario(
                    username=data["username"],
                    nombre_completo=data["nombre_completo"],
                    nombre_normalizado=nombre_norm,
                    password_hash=hash_password(data["password"]),
                    rol=data["rol"],
                    activo=True,
                )
            )
            print(f"  Usuario '{data['username']}' creado ({data['rol']}).")

        db.commit()
    finally:
        db.close()
