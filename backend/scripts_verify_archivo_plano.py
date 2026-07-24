"""Verifica que el archivo plano alinee con el modelo Excel del banco."""
from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

from app.services.archivo_plano_service import (
    _parte_importe,
    _ruta_pago,
    build_payment_line,
)


def _pago(**kwargs):
    defaults = {
        "tipo_identificacion": 1,
        "identificacion": "91492808",
        "digito_verificacion": 0,
        "forma_pago": 1,
        "banco_codigo": 51,
        "cod_oficina": None,
        "numero_cuenta": "046570046204",
        "importe": Decimal("3000000.00"),
        "razon_social": "JUAN FERNANDO GUARIN",
        "concepto1": "ANTICIPO",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def main() -> None:
    excel = (
        "01000000091492808010051000000000000000002046570046204     "
        "000000300000000000000000000JUAN FERNANDO GUARIN                BOGOTA"
    )
    # El Excel de referencia usa cuenta 2046570046204; replicamos esa estructura.
    pago_excel_cuenta = _pago(numero_cuenta="2046570046204")
    linea = build_payment_line(pago_excel_cuenta, ciudad="BOGOTA")

    assert _ruta_pago(pago_excel_cuenta) == "010051", _ruta_pago(pago_excel_cuenta)
    assert linea[17:23] == "010051", repr(linea[17:23])
    assert "000000300000000" in linea, "importe 3.000.000 en centavos no encontrado"
    assert linea.startswith("01000000091492808"), repr(linea[:17])
    assert "JUAN FERNANDO GUARIN" in linea
    assert "ANTICIPO" in linea
    assert "\n" not in linea and "\r" not in linea

    # Misma estructura de forma/banco/ceros que el Excel hasta la cuenta
    assert linea[17:39] == excel[17:39], (
        f"desfase forma/banco/ceros\nprog={linea[17:39]!r}\nexcel={excel[17:39]!r}"
    )

    # Caso típico de la prueba fallida (cuenta 046570046204)
    pago_prueba = _pago(numero_cuenta="046570046204", razon_social="JUAN FERNADO GUARIN CASTRO")
    linea2 = build_payment_line(pago_prueba, ciudad="BOGOTA")
    assert linea2[17:23] == "010051"
    assert "000000300000000" in linea2
    # Ya NO debe empezar la ruta con un solo dígito '1' tras la identificación
    assert not linea2[17:].startswith("10051"), "sigue el bug de 1 dígito en forma de pago"

    # Con oficina: ruta de 10 caracteres y línea válida
    pago_of = _pago(cod_oficina="1234")
    assert len(_ruta_pago(pago_of)) == 10
    assert _ruta_pago(pago_of) == "0100511234"
    linea_of = build_payment_line(pago_of, ciudad="BOGOTA")
    assert linea_of.startswith("01000000091492808")
    assert linea_of[17:27] == "0100511234"
    assert "000000300000000" in linea_of
    p2, p3 = _parte_importe(_ruta_pago(pago_of), "046570046204", 300000000)
    assert len(p3) == 30
    assert len(p2) <= 37

    print("OK — archivo plano alineado con modelo Excel (forma_pago 2 dígitos)")
    print("Muestra línea (primeros 90):")
    print(linea[:90])
    print("Importe embebido:", "000000300000000" if "000000300000000" in linea else "ERROR")


if __name__ == "__main__":
    main()
