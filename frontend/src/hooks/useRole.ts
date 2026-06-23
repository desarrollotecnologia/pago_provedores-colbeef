import { useAuth } from "../context/AuthContext";

export function useRole() {
  const { user } = useAuth();
  const isAdmin = user?.rol === "admin";
  const isOperador = user?.rol === "operador";
  return { user, isAdmin, isOperador };
}
