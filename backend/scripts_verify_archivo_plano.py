"""Verifica el generador contra la macro Planocash del Excel BBVA."""
from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

from app.services.archivo_plano_service import build_payment_line


def _pago(**kwargs):
    defaults = {
        "tipo_identificacion": 1,
        "identificacion": "91492808",
        "digito_verificacion": 0,
        "forma_pago": 1,
        "banco_codigo": 51,
        "tipo_cuenta": 2,
        "cod_oficina": None,
        "numero_cuenta": "046570046204",
        "importe": Decimal("3000000.00"),
        "razon_social": "JUAN FERNANDO GUARIN",
        "concepto1": "ANTICIPO",
        "concepto2": None,
        "concepto3": None,
        "concepto4": None,
        "email_destino": "jugua7612@hotmail.com",
        "fecha_limite": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def main() -> None:
    # Línea de referencia del Excel (tipo cuenta con formato 00 → '02')
    excel_prefix = (
        "01000000091492808010051"
        "0000000000000000"
        "02"
        "046570046204     "
        "000000300000000"
    )

    linea = build_payment_line(
        _pago(numero_cuenta="046570046204", tipo_cuenta=2),
        ciudad="BOGOTA",
    )

    assert linea.startswith(excel_prefix), (
        f"prefijo distinto\nprog ={linea[: len(excel_prefix)]!r}\nexcel={excel_prefix!r}"
    )
    assert "JUAN FERNANDO GUARIN" in linea
    assert "BOGOTA" in linea
    assert "jugua7612@hotmail.com" in linea
    assert "ANTICIPO" in linea
    assert "\n" not in linea and "\r" not in linea

    # NIT con DV distinto de 0: DV + forma 1 dígito + banco 4
    nit = build_payment_line(
        _pago(
            tipo_identificacion=3,
            identificacion="900373913",
            digito_verificacion=4,
            tipo_cuenta=1,
            numero_cuenta="12345678901",
            banco_codigo=7,
        ),
        ciudad="BOGOTA",
    )
    assert nit.startswith("03000000900373913410007"), nit[:30]
    assert "01" == nit[39:41], nit[39:45]  # tipo cuenta 01

    # BBVA (banco 0013): bloque Cuentabbva de 16 caracteres sin cero de relleno al final
    bbva_cases = [
        ("232217414", 2, "0232000200217414"),
        ("474012663", 1, "0474000100012663"),
        ("018117200", 2, "0018000200117200"),
    ]
    for numero_cuenta, tipo_cuenta, cuentabbva_esperada in bbva_cases:
        linea_bbva = build_payment_line(
            _pago(
                banco_codigo=13,
                tipo_cuenta=tipo_cuenta,
                numero_cuenta=numero_cuenta,
            ),
            ciudad="BOGOTA",
        )
        assert linea_bbva[19:23] == "0013", linea_bbva[19:23]
        assert linea_bbva[23:39] == cuentabbva_esperada, (
            f"cuenta={numero_cuenta} tipo={tipo_cuenta}\n"
            f"prog ={linea_bbva[23:39]!r}\nexcel={cuentabbva_esperada!r}"
        )
        assert linea_bbva[39:41] == "00", linea_bbva[39:41]
        assert linea_bbva[41:58] == "0" * 17, linea_bbva[41:58]

    print("OK — generador alineado con macro Planocash / Excel BBVA")
    print("Longitud línea:", len(linea))
    print("Prefijo:", linea[:80])
    print("Email embebido:", "jugua7612@hotmail.com" in linea)


if __name__ == "__main__":
    main()
