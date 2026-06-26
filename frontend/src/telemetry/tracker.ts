/**
 * Tracker ligero de usabilidad — no bloquea la UI.
 */
import { api } from "../api/client";
import { getToken } from "../auth/session";

export type UsabilityAction =
  | "session_start"
  | "module_open"
  | "action_complete"
  | "error_ui"
  | "admin_open";

const ROUTE_MODULES: Record<string, string> = {
  "/": "inicio",
  "/proveedores": "proveedores",
  "/pagos": "pagos",
  "/historial": "historial",
  "/config": "configuracion",
  "/usabilidad": "usabilidad",
};

let memorySessionId: string | null = null;
let sessionStarted = false;
const pendingRetries = new Set<string>();

function createSessionId(): string {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  const random = Math.random().toString(36).slice(2, 12);
  return `${Date.now().toString(36)}-${random}`;
}

export function getSessionId(): string {
  if (!memorySessionId) {
    memorySessionId = createSessionId();
  }
  return memorySessionId;
}

export function clearTelemetrySession(): void {
  memorySessionId = null;
  sessionStarted = false;
  pendingRetries.clear();
}

function canTrack(): boolean {
  return Boolean(getToken());
}

type EventBody = {
  session_id: string;
  action: UsabilityAction;
  module: string;
  detail?: string;
  page?: string;
  meta?: Record<string, unknown>;
};

function buildEvent(
  action: UsabilityAction,
  module: string,
  detail?: string,
  meta?: Record<string, unknown>
): EventBody {
  const safeMeta = meta
    ? Object.fromEntries(
        Object.entries(meta).filter(
          ([k]) => !["password", "token", "secret", "access_token"].includes(k.toLowerCase())
        )
      )
    : undefined;

  return {
    session_id: getSessionId(),
    action,
    module,
    detail: detail?.slice(0, 255),
    page: window.location.pathname,
    meta: safeMeta && Object.keys(safeMeta).length ? safeMeta : undefined,
  };
}

function eventKey(body: EventBody): string {
  return `${body.session_id}:${body.action}:${body.module}:${body.detail ?? ""}:${body.page ?? ""}`;
}

async function sendEvent(body: EventBody): Promise<void> {
  await api.usabilityEvent(body);
}

function scheduleRetry(body: EventBody): void {
  const key = eventKey(body);
  if (pendingRetries.has(key)) return;
  pendingRetries.add(key);
  window.setTimeout(() => {
    pendingRetries.delete(key);
    if (!canTrack()) return;
    sendEvent(body).catch(() => {
      /* segundo intento fallido — no bloquear UX */
    });
  }, 2500);
}

export function track(
  action: UsabilityAction,
  module: string,
  detail?: string,
  meta?: Record<string, unknown>
): void {
  try {
    if (!canTrack()) return;
    const body = buildEvent(action, module, detail, meta);
    sendEvent(body).catch(() => scheduleRetry(body));
  } catch {
    /* silencioso — el tracking no debe romper la app */
  }
}

export function trackSessionStart(rol: string): void {
  try {
    if (sessionStarted) return;
    sessionStarted = true;
    track("session_start", "auth", `Inicio de sesión (${rol})`);
  } catch {
    /* silencioso — no interferir con login */
  }
}

export function trackModuleFromPath(pathname: string): void {
  let module = ROUTE_MODULES[pathname];
  if (!module && pathname.startsWith("/pagos/")) {
    module = "lote_detalle";
  }
  if (!module) module = "otro";
  track("module_open", module, `Pantalla: ${pathname}`);
}

export function trackAction(module: string, detail: string, meta?: Record<string, unknown>): void {
  track("action_complete", module, detail, meta);
}

export function trackError(module: string, detail: string): void {
  track("error_ui", module, detail);
}

/** Atajo oculto: Ctrl+Shift+U → dashboard usabilidad (solo admin en router) */
export function bindUsabilityShortcut(onTrigger: () => void): () => void {
  const handler = (e: KeyboardEvent) => {
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "u") {
      e.preventDefault();
      onTrigger();
    }
  };
  window.addEventListener("keydown", handler);
  return () => window.removeEventListener("keydown", handler);
}
