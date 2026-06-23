"""Verifica el estado de la base de datos."""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine, text

from app.core.config import get_settings


def main() -> None:
    engine = create_engine(get_settings().database_url)
    with engine.connect() as conn:
        print("=== Estado de la base de datos ===")
        for table in [
            "usuarios",
            "bancos",
            "oficinas_banco",
            "cuentas_ordenantes",
            "proveedores",
            "lotes_pago",
            "pagos",
        ]:
            n = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table:20} {n:>6}")

        print("\nUsuarios:")
        for row in conn.execute(text("SELECT username, rol FROM usuarios")):
            print(f"  - {row.username} ({row.rol})")


if __name__ == "__main__":
    main()
