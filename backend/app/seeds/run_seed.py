"""
Script principal de inicialización - Fase 1.
Crea tablas, catálogos, usuarios y importa datos del Excel.

Uso:
    python -m app.seeds.run_seed
    python -m app.seeds.run_seed --excel "ruta\\al\\archivo.xls"
    python -m app.seeds.run_seed --skip-excel
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Asegurar que backend esté en el path
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.seeds.import_excel import import_from_excel
from app.seeds.seed_catalogos import seed_catalogos
from app.seeds.seed_usuarios import seed_usuarios
from app.seeds.setup_database import create_database_if_not_exists, create_tables


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicializar BD - Fase 1")
    parser.add_argument("--excel", help="Ruta al archivo Excel operativo")
    parser.add_argument("--skip-excel", action="store_true", help="Omitir importación Excel")
    parser.add_argument("--skip-create-db", action="store_true", help="No crear la BD")
    args = parser.parse_args()

    print("=" * 60)
    print("PAGO PROVEEDORES - Inicialización Fase 1")
    print("=" * 60)

    if not args.skip_create_db:
        print("\n[1/5] Creando base de datos si no existe...")
        create_database_if_not_exists()

    print("\n[2/5] Creando tablas...")
    create_tables()

    print("\n[3/5] Cargando catálogos y configuración...")
    seed_catalogos()

    print("\n[4/5] Creando usuarios iniciales...")
    seed_usuarios()

    if not args.skip_excel:
        print("\n[5/5] Importando datos desde Excel...")
        stats = import_from_excel(args.excel)
        print(f"  Bancos importados:      {stats['bancos']}")
        print(f"  Oficinas importadas:    {stats['oficinas']}")
        print(f"  Cuentas ordenantes:     {stats['cuentas']}")
        print(f"  Proveedores importados: {stats['proveedores']}")
        print(f"  Proveedores omitidos:   {stats['omitidos']}")
    else:
        print("\n[5/5] Importación Excel omitida (--skip-excel)")

    print("\n" + "=" * 60)
    print("Inicialización completada correctamente.")
    print("=" * 60)


if __name__ == "__main__":
    main()
