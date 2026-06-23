/** Token en sessionStorage: persiste al recargar, no al compartir enlace en otro navegador. */
const TOKEN_KEY = "pp_token";

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY);
}

export function clearSession(): void {
  clearToken();
  sessionStorage.removeItem("usability_session_id");
  sessionStorage.removeItem("usability_session_started");
}
