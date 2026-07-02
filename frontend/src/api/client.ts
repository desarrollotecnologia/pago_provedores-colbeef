import type {
  BancoCatalogo,
  CatalogoItem,
  CuentaOrdenante,
  DashboardResponse,
  HistorialPagoDetalle,
  HistorialPagosResponse,
  CambioProveedorDetalle,
  CambiosProveedorResponse,
  Lote,
  LoteListItem,
  Paginated,
  ProcesarLoteResponse,
  Proveedor,
  PublicConfig,
  SmtpStatus,
  TokenResponse,
  UsabilityStats,
  UsuarioAuth,
} from "../types";

import { getToken, setToken, clearSession } from "../auth/session";

const API = "/api";

let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit & { silentAuth?: boolean } = {}
): Promise<T> {
  const { silentAuth, ...fetchOptions } = options;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API}${path}`, { ...fetchOptions, headers });
  if (res.status === 401) {
    const isLogin = path === "/auth/login" || path.endsWith("/auth/login");
    if (!isLogin && !silentAuth) {
      clearSession();
      onUnauthorized?.();
    }
    throw new ApiError("Sesión expirada o no autorizada", 401);
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? body.message ?? detail;
      if (Array.isArray(detail)) detail = detail.map((d) => d.msg ?? d).join(", ");
    } catch {
      /* ignore */
    }
    throw new ApiError(String(detail), res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  login(usuario: string, password: string) {
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ usuario, password }),
    });
  },

  me() {
    return request<UsuarioAuth & { activo: boolean }>("/auth/me");
  },

  config() {
    return request<PublicConfig>("/config");
  },

  dashboard(params?: { fecha_desde?: string; fecha_hasta?: string }) {
    const q = new URLSearchParams();
    if (params?.fecha_desde) q.set("fecha_desde", params.fecha_desde);
    if (params?.fecha_hasta) q.set("fecha_hasta", params.fecha_hasta);
    const qs = q.toString();
    return request<DashboardResponse>(`/dashboard${qs ? `?${qs}` : ""}`);
  },

  async historialPagos(params: {
    fecha_desde: string;
    fecha_hasta: string;
    page?: number;
    page_size?: number;
    q?: string;
  }) {
    const q = new URLSearchParams({
      fecha_desde: params.fecha_desde,
      fecha_hasta: params.fecha_hasta,
      // Compatibilidad con backend anterior que solo aceptaba ?fecha=
      fecha: params.fecha_desde,
    });
    if (params.page) q.set("page", String(params.page));
    if (params.page_size) q.set("page_size", String(params.page_size));
    if (params.q) q.set("q", params.q);
    const qs = q.toString();
    const paths = [`/historial/pagos?${qs}`, `/lotes/historial/pagos?${qs}`];
    let lastError: ApiError | null = null;
    for (const path of paths) {
      try {
        return await request<HistorialPagosResponse>(path);
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          lastError = err;
          continue;
        }
        throw err;
      }
    }
    throw lastError ?? new ApiError("Historial no disponible", 404);
  },

  async historialPagoDetalle(id: number) {
    const paths = [`/historial/pagos/${id}`, `/lotes/historial/pagos/${id}`];
    let lastError: ApiError | null = null;
    for (const path of paths) {
      try {
        return await request<HistorialPagoDetalle>(path);
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          lastError = err;
          continue;
        }
        throw err;
      }
    }
    throw lastError ?? new ApiError("Pago no encontrado", 404);
  },

  cambiosProveedores(params: {
    fecha_desde: string;
    fecha_hasta: string;
    page?: number;
    page_size?: number;
    q?: string;
  }) {
    const q = new URLSearchParams({
      fecha_desde: params.fecha_desde,
      fecha_hasta: params.fecha_hasta,
      fecha: params.fecha_desde,
    });
    if (params.page) q.set("page", String(params.page));
    if (params.page_size) q.set("page_size", String(params.page_size));
    if (params.q) q.set("q", params.q);
    return request<CambiosProveedorResponse>(`/cambios/proveedores?${q.toString()}`);
  },

  cambioProveedorDetalle(id: number) {
    return request<CambioProveedorDetalle>(`/cambios/proveedores/${id}`);
  },

  smtpStatus() {
    return request<SmtpStatus>("/config/smtp-status");
  },

  cuentasOrdenantes() {
    return request<CuentaOrdenante[]>("/cuentas-ordenantes");
  },

  bancos() {
    return request<BancoCatalogo[]>("/catalogos/bancos");
  },

  tiposIdentificacion() {
    return request<CatalogoItem[]>("/catalogos/tipos-identificacion");
  },

  tiposCuenta() {
    return request<CatalogoItem[]>("/catalogos/tipos-cuenta");
  },

  proveedores(params: Record<string, string | number | boolean | undefined> = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") q.set(k, String(v));
    });
    return request<Paginated<Proveedor>>(`/proveedores?${q}`);
  },

  proveedor(id: number) {
    return request<Proveedor>(`/proveedores/${id}`);
  },

  crearProveedor(data: object) {
    return request<Proveedor>("/proveedores", { method: "POST", body: JSON.stringify(data) });
  },

  actualizarProveedor(id: number, data: object) {
    return request<Proveedor>(`/proveedores/${id}`, { method: "PUT", body: JSON.stringify(data) });
  },

  desactivarProveedor(id: number) {
    return request<{ message: string }>(`/proveedores/${id}`, { method: "DELETE" });
  },

  lotes(params: Record<string, string | number | undefined> = {}) {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") q.set(k, String(v));
    });
    return request<Paginated<LoteListItem>>(`/lotes?${q}`);
  },

  lote(id: number) {
    return request<Lote>(`/lotes/${id}`);
  },

  crearLote(data: object) {
    return request<Lote>("/lotes", { method: "POST", body: JSON.stringify(data) });
  },

  actualizarLote(id: number, data: object) {
    return request<Lote>(`/lotes/${id}`, { method: "PUT", body: JSON.stringify(data) });
  },

  confirmarLote(id: number) {
    return request<Lote>(`/lotes/${id}/confirmar`, { method: "POST" });
  },

  agregarPago(loteId: number, data: object) {
    return request(`/lotes/${loteId}/pagos`, { method: "POST", body: JSON.stringify(data) });
  },

  actualizarPago(pagoId: number, data: object) {
    return request(`/lotes/pagos/${pagoId}`, { method: "PUT", body: JSON.stringify(data) });
  },

  eliminarPago(pagoId: number) {
    return request(`/lotes/pagos/${pagoId}`, { method: "DELETE" });
  },

  generarArchivo(loteId: number) {
    return request<ProcesarLoteResponse>(`/lotes/${loteId}/generar-archivo`, { method: "POST" });
  },

  enviarCorreos(loteId: number) {
    return request<ProcesarLoteResponse>(`/lotes/${loteId}/enviar-correos`, { method: "POST" });
  },

  procesarLote(loteId: number, enviarCorreos = true) {
    return request<ProcesarLoteResponse>(
      `/lotes/${loteId}/procesar?enviar_correos=${enviarCorreos}`,
      { method: "POST" }
    );
  },

  descargarArchivoUrl(loteId: number) {
    return `${API}/lotes/${loteId}/descargar-archivo`;
  },

  usabilityStats(days = 30) {
    return request<UsabilityStats>(`/usability/stats?days=${days}`);
  },

  usabilityEvent(payload: {
    session_id: string;
    action: string;
    module: string;
    detail?: string;
    page?: string;
    meta?: Record<string, unknown>;
  }) {
    return request<{ id: number; message: string }>("/usability/event", {
      method: "POST",
      body: JSON.stringify(payload),
      silentAuth: true,
    });
  },
};

export { ApiError, getToken, setToken, clearSession };
