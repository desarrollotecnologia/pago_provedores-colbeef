"""Zona horaria operativa del sistema (Colombia)."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

BOGOTA = ZoneInfo("America/Bogota")


def today_colombia() -> date:
    return datetime.now(BOGOTA).date()
