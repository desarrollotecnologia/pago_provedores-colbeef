from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Banco(Base):
    __tablename__ = "bancos"

    codigo: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(100), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class OficinaBanco(Base):
    __tablename__ = "oficinas_banco"

    codigo: Mapped[str] = mapped_column(String(10), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)


class TipoIdentificacion(Base):
    __tablename__ = "tipos_identificacion"

    codigo: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(50), nullable=False)


class TipoCuenta(Base):
    __tablename__ = "tipos_cuenta"

    codigo: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(30), nullable=False)


class CuentaOrdenante(Base):
    __tablename__ = "cuentas_ordenantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_cuenta: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    alias: Mapped[str] = mapped_column(String(50), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    nombre_normalizado: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(
        Enum("admin", "operador", name="rol_usuario"), default="operador", nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    lotes: Mapped[list["LotePago"]] = relationship(back_populates="usuario")


class Proveedor(Base):
    __tablename__ = "proveedores"
    __table_args__ = (
        UniqueConstraint("identificacion", "tipo_identificacion", name="uk_identificacion"),
        Index("idx_razon_social", "razon_social"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    identificacion: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_identificacion: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("tipos_identificacion.codigo"), nullable=False
    )
    digito_verificacion: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    razon_social: Mapped[str] = mapped_column(String(200), nullable=False)
    forma_pago: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    banco_codigo: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("bancos.codigo"), nullable=False
    )
    tipo_cuenta: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("tipos_cuenta.codigo"), nullable=False
    )
    numero_cuenta: Mapped[str] = mapped_column(String(20), nullable=False)
    cod_oficina: Mapped[str | None] = mapped_column(String(10), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    banco: Mapped["Banco"] = relationship()
    pagos: Mapped[list["Pago"]] = relationship(back_populates="proveedor")


class LotePago(Base):
    __tablename__ = "lotes_pago"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_operacion: Mapped[datetime] = mapped_column(Date, nullable=False)
    fecha_limite: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    cuenta_ordenante_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cuentas_ordenantes.id"), nullable=False
    )
    concepto_general: Mapped[str] = mapped_column(String(120), nullable=False)
    estado: Mapped[str] = mapped_column(
        Enum(
            "borrador",
            "confirmado",
            "archivo_generado",
            "correos_enviados",
            "completado",
            "anulado",
            name="estado_lote",
        ),
        default="borrador",
        nullable=False,
    )
    importe_total: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), default=Decimal("0.00"), nullable=False
    )
    cantidad_pagos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    archivo_plano_nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    archivo_plano_ruta: Mapped[str | None] = mapped_column(String(500), nullable=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="lotes")
    cuenta_ordenante: Mapped["CuentaOrdenante"] = relationship()
    pagos: Mapped[list["Pago"]] = relationship(
        back_populates="lote", cascade="all, delete-orphan"
    )


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lote_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lotes_pago.id", ondelete="CASCADE"), nullable=False
    )
    proveedor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("proveedores.id"), nullable=False
    )
    identificacion: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_identificacion: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    digito_verificacion: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    razon_social: Mapped[str] = mapped_column(String(200), nullable=False)
    banco_codigo: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("bancos.codigo"), nullable=False
    )
    tipo_cuenta: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    numero_cuenta: Mapped[str] = mapped_column(String(20), nullable=False)
    cod_oficina: Mapped[str | None] = mapped_column(String(10), nullable=True)
    forma_pago: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    importe: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    fecha_limite: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    concepto1: Mapped[str | None] = mapped_column(String(80), nullable=True)
    concepto2: Mapped[str | None] = mapped_column(String(80), nullable=True)
    concepto3: Mapped[str | None] = mapped_column(String(80), nullable=True)
    concepto4: Mapped[str | None] = mapped_column(String(80), nullable=True)
    numero_factura: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email_destino: Mapped[str | None] = mapped_column(String(255), nullable=True)
    referencia_16: Mapped[str | None] = mapped_column(String(20), nullable=True)
    referencia_11: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estado: Mapped[str] = mapped_column(
        Enum(
            "pendiente",
            "incluido_archivo",
            "correo_enviado",
            "correo_error",
            "anulado",
            name="estado_pago",
        ),
        default="pendiente",
        nullable=False,
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    lote: Mapped["LotePago"] = relationship(back_populates="pagos")
    proveedor: Mapped["Proveedor"] = relationship(back_populates="pagos")
    envios_correo: Mapped[list["EnvioCorreo"]] = relationship(back_populates="pago")


class EnvioCorreo(Base):
    __tablename__ = "envios_correo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pago_id: Mapped[int] = mapped_column(Integer, ForeignKey("pagos.id"), nullable=False)
    destinatario: Mapped[str] = mapped_column(String(255), nullable=False)
    asunto: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(
        Enum("enviado", "error", "pendiente", name="estado_correo"),
        nullable=False,
    )
    mensaje_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    enviado_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    pago: Mapped["Pago"] = relationship(back_populates="envios_correo")


class Configuracion(Base):
    __tablename__ = "configuracion"

    clave: Mapped[str] = mapped_column(String(100), primary_key=True)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)


class EventoUsabilidad(Base):
    __tablename__ = "eventos_usabilidad"
    __table_args__ = (
        Index("idx_usabilidad_timestamp", "timestamp"),
        Index("idx_usabilidad_usuario", "usuario"),
        Index("idx_usabilidad_action", "action"),
        Index("idx_usabilidad_module", "module"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    usuario: Mapped[str] = mapped_column(String(80), nullable=False)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    module: Mapped[str] = mapped_column(String(60), nullable=False)
    detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    page: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
