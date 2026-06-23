/**
 * Tracker ligero de usabilidad — no bloquea la UI.
 * No registrar contraseñas, tokens ni datos sensibles.
 */

export type UsabilityAction =
  | "session_start"
  | "module_open"
  | "action_complete"
  | "error_ui"
  | "admin_open";

const SESSION_KEY = "usability_session_id";
const SESSION_STARTED_KEY = "usability_session_started";

const ROUTE_MODULES: Record<string, string> = {
  "/": "inicio",
  "/proveedores": "proveedores",
  "/pagos": "pagos",
  "/config": "configuracion",
  "/usabilidad": "usabilidad",
};

export function getSessionId(): string {
  let id = sessionStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

function canTrack(): boolean {
  return Boolean(localStorage.getItem("token"));
}

export function track(
  action: UsabilityAction,
  module: string,
  detail?: string,
  meta?: Record<string, unknown>
): void {
  if (!canTrack()) return;

  const safeMeta = meta
    ? Object.fromEntries(
        Object.entries(meta).filter(
          ([k]) => !["password", "token", "secret", "access_token"].includes(k.toLowerCase())
        )
      )
    : undefined;

  const body = {
    session_id: getSessionId(),
    action,
    module,
    detail: detail?.slice(0, 255),
    page: window.location.pathname,
    meta: safeMeta,
    timestamp: new Date().toISOString(),
  };

  fetch("/api/usability/event", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
    body: JSON.stringify(body),
    keepalive: true,
  }).catch(() => {
    /* silencioso — no interferir con UX */
  });
}

export function trackSessionStart(rol: string): void {
  if (sessionStorage.getItem(SESSION_STARTED_KEY)) return;
  sessionStorage.setItem(SESSION_STARTED_KEY, "1");
  track("session_start", "auth", `Inicio de sesión (${rol})`);
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
