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

export function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

export function statusClass(estado: string) {
  return `status-badge status-${estado.replace(/\s/g, "_")}`;
}
