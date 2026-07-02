export function formatMoney(value: string | number) {
  const n = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(n || 0);
}

export function formatDate(value: string | null) {
  if (!value) return "—";
  return new Date(value + "T00:00:00").toLocaleDateString("es-CO");
}

export function formatDateTime(value: string | null) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function accionCambioLabel(accion: string) {
  if (accion === "crear") return "Creación";
  if (accion === "editar") return "Edición";
  if (accion === "desactivar") return "Desactivación";
  return accion;
}

export function accionCambioClass(accion: string) {
  return `cambio-accion cambio-accion-${accion}`;
}

export function todayISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function offsetDateISO(days: number) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function isSameDayISO(a: string | null | undefined, b: string) {
  if (!a) return false;
  return a.slice(0, 10) === b.slice(0, 10);
}

export function statusClass(estado: string) {
  return `status-badge status-${estado.replace(/\s/g, "_")}`;
}
