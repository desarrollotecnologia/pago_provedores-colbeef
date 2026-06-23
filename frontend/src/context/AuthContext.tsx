import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, setUnauthorizedHandler } from "../api/client";
import { clearSession, getToken, setToken } from "../auth/session";
import { trackSessionStart } from "../telemetry/tracker";
import type { PublicConfig, UsuarioAuth } from "../types";

interface AuthState {
  user: UsuarioAuth | null;
  config: PublicConfig | null;
  loading: boolean;
  login: (usuario: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UsuarioAuth | null>(null);
  const [config, setConfig] = useState<PublicConfig | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setUser(null);
    });
  }, []);

  useEffect(() => {
    api.config().then(setConfig).catch(() => null);
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .me()
      .then((u) => {
        setUser(u);
        trackSessionStart(u.rol);
      })
      .catch(() => {
        clearSession();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (usuario: string, password: string) => {
    const res = await api.login(usuario, password);
    setToken(res.access_token);
    setUser(res.usuario);
    trackSessionStart(res.usuario.rol);
  }, []);

  const value = useMemo(
    () => ({ user, config, loading, login, logout }),
    [user, config, loading, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside provider");
  return ctx;
}
