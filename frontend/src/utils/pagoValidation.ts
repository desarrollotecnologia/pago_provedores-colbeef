import type { Pago } from "../types";

export interface PagoFormData {
  importe: string;
  numero_factura: string;
  concepto1: string;
  email_destino: string;
}

export function camposFaltantesPago(data: PagoFormData): string[] {
  const faltantes: string[] = [];
  const importe = parseFloat(data.importe);
  if (!data.importe || Number.isNaN(importe) || importe <= 0) faltantes.push("importe");
  if (!data.numero_factura.trim()) faltantes.push("número de factura");
  if (!data.concepto1.trim()) faltantes.push("concepto");
  if (!data.email_destino.trim()) faltantes.push("email destino");
  return faltantes;
}

export function pagoIncompleto(p: Pago): boolean {
  const importe = parseFloat(p.importe);
  if (!importe || importe <= 0) return true;
  if (!p.numero_factura?.trim()) return true;
  if (!p.concepto1?.trim()) return true;
  if (!p.email_destino?.trim()) return true;
  return false;
}

export function mensajeCamposFaltantes(faltantes: string[]): string {
  return `Complete los campos obligatorios: ${faltantes.join(", ")}`;
}
