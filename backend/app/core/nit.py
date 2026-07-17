"""Cálculo del dígito de verificación de NIT colombiano (DIAN)."""

import re

TIPOS_IDENTIFICACION_NIT = frozenset({3, 9})

_PESOS_DIAN = (71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3)


def normalizar_numero_nit(identificacion: str) -> str:
    """Devuelve solo el número base; retira un DV escrito después de guion."""
    valor = str(identificacion).strip()
    nit_con_dv = re.fullmatch(r"(.*\d)\s*-\s*\d", valor)
    if nit_con_dv:
        valor = nit_con_dv.group(1)
    return "".join(caracter for caracter in valor if caracter.isdigit())


def calcular_digito_verificacion_nit(identificacion: str) -> int:
    """Calcula el DV usando los dígitos del NIT, sin incluir un DV existente."""
    digitos = normalizar_numero_nit(identificacion)
    if not digitos:
        raise ValueError("El NIT debe contener al menos un dígito")
    if len(digitos) > len(_PESOS_DIAN):
        raise ValueError("El NIT no puede tener más de 15 dígitos")

    pesos = _PESOS_DIAN[-len(digitos) :]
    residuo = sum(int(digito) * peso for digito, peso in zip(digitos, pesos)) % 11
    return residuo if residuo in (0, 1) else 11 - residuo
