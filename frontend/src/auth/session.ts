/**
 * Sesión solo en memoria (RAM).
 * No persiste al recargar ni al abrir otra pestaña — requiere login cada vez.
 */
const TOKEN_KEY = "pp_token";
const LEGACY_TOKEN_KEY = "token";

let memoryToken: string | null = null;

export function getToken(): string | null {
  return memoryToken;
}

export function setToken(token: string): void {
  memoryToken = token;
}

export function clearToken(): void {
  memoryToken = null;
}

/** Elimina tokens viejos que pudieran quedar en el navegador de versiones anteriores. */
export function purgeLegacyAuthStorage(): void {
  try {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem("usability_session_id");
    sessionStorage.removeItem("usability_session_started");
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(LEGACY_TOKEN_KEY);
    localStorage.removeItem("usability_session_id");
    localStorage.removeItem("usability_session_started");
  } catch {
    /* ignore */
  }
}

export function clearSession(): void {
  clearToken();
  purgeLegacyAuthStorage();
}
