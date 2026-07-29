import type { Pago } from "../types";

export interface PagoFormData {
  importe: string;
  facturas: string[];
  concepto1: string;
  email_destino: string;
}

export function splitFacturas(valor: string | null | undefined): string[] {
  if (!valor?.trim()) return [];
  const seen = new Set<string>();
  const out: string[] = [];
  for (const part of valor.replace(/[;|]/g, ",").split(",")) {
    const t = part.trim();
    if (!t) continue;
    const key = t.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(t);
  }
  return out;
}

export function facturasFromPago(p: Pago): string[] {
  if (p.facturas?.length) return p.facturas.map((f) => f.trim()).filter(Boolean);
  return splitFacturas(p.numero_factura);
}

export function camposFaltantesPago(data: PagoFormData): string[] {
  const faltantes: string[] = [];
  const importe = parseFloat(data.importe);
  if (!data.importe || Number.isNaN(importe) || importe <= 0) faltantes.push("importe");
  const facturas = data.facturas.map((f) => f.trim()).filter(Boolean);
  if (!facturas.length) faltantes.push("al menos una factura");
  if (!data.concepto1.trim()) faltantes.push("concepto");
  if (!data.email_destino.trim()) faltantes.push("email destino");
  return faltantes;
}

export function pagoIncompleto(p: Pago): boolean {
  const importe = parseFloat(p.importe);
  if (!importe || importe <= 0) return true;
  if (!facturasFromPago(p).length) return true;
  if (!p.concepto1?.trim()) return true;
  if (!p.email_destino?.trim()) return true;
  return false;
}

export function mensajeCamposFaltantes(faltantes: string[]): string {
  return `Complete los campos obligatorios: ${faltantes.join(", ")}`;
}
