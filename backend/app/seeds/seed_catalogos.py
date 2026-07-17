"""Carga catálogos estáticos y configuración del sistema."""
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Configuracion, TipoCuenta, TipoIdentificacion
from app.seeds.setup_database import create_resumen_view

# Códigos según formato bancario (Excel MODELO PAGO PROVEEDORES)
TIPOS_IDENTIFICACION = [
    (1, "Cédula de Ciudadanía"),
    (2, "Cédula de Extranjería"),
    (3, "NIT Jurídico"),
    (4, "Tarjeta de Identidad"),
    (5, "Pasaporte"),
    (6, "NIT Extranjería"),
    (7, "Soc. Extranjera Sin NIT Colombia"),
    (8, "Fideicomiso"),
    (9, "NIT Natural"),
]

TIPOS_CUENTA = [
    (1, "Ahorros"),
    (2, "Corriente"),
]

CONFIGURACION_INICIAL = [
    ("smtp_host", "", "Servidor SMTP colbeef.com"),
    ("smtp_port", "587", "Puerto SMTP"),
    ("smtp_user", "coordinacion.tesoreria@colbeef.com", "Usuario SMTP"),
    ("smtp_password", "", "Contraseña SMTP"),
    ("smtp_from_name", "Coordinación Tesorería", "Nombre remitente"),
    ("ciudad_default", "BOGOTA", "Ciudad en archivo plano"),
    ("concepto_campo_factura", "concepto1", "Campo que mapea al N° factura en correo"),
]


def seed_catalogos() -> None:
    db = SessionLocal()
    try:
        for codigo, descripcion in TIPOS_IDENTIFICACION:
            exists = db.scalar(
                select(TipoIdentificacion).where(TipoIdentificacion.codigo == codigo)
            )
            if not exists:
                db.add(TipoIdentificacion(codigo=codigo, descripcion=descripcion))
            elif exists.descripcion != descripcion:
                # Corrige etiquetas antiguas (p. ej. "NIT" → "NIT Jurídico", "Otro" → "NIT Natural")
                exists.descripcion = descripcion

        for codigo, descripcion in TIPOS_CUENTA:
            exists = db.scalar(select(TipoCuenta).where(TipoCuenta.codigo == codigo))
            if not exists:
                db.add(TipoCuenta(codigo=codigo, descripcion=descripcion))

        for clave, valor, descripcion in CONFIGURACION_INICIAL:
            exists = db.scalar(select(Configuracion).where(Configuracion.clave == clave))
            if not exists:
                db.add(Configuracion(clave=clave, valor=valor, descripcion=descripcion))

        db.commit()
        create_resumen_view()
    finally:
        db.close()
