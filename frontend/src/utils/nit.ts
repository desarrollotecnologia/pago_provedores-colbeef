export const TIPOS_IDENTIFICACION_NIT = new Set([3, 9]);

const PESOS_DIAN = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3];

export function normalizarNumeroNit(identificacion: string): string {
  const valor = identificacion.trim().replace(/(.*\d)\s*-\s*\d$/, "$1");
  return valor.replace(/\D/g, "");
}

export function calcularDigitoVerificacionNit(identificacion: string): number | null {
  const digitos = normalizarNumeroNit(identificacion);
  if (!digitos || digitos.length > PESOS_DIAN.length) return null;

  const pesos = PESOS_DIAN.slice(-digitos.length);
  const residuo =
    [...digitos].reduce((total, digito, indice) => total + Number(digito) * pesos[indice], 0) %
    11;

  return residuo === 0 || residuo === 1 ? residuo : 11 - residuo;
}
