import { Navigate } from "react-router-dom";
import { useRole } from "../hooks/useRole";

/** Solo usuario operador (panel) — estadísticas de usabilidad. */
export default function OperadorRoute({ children }: { children: React.ReactNode }) {
  const { isOperador } = useRole();
  if (!isOperador) return <Navigate to="/" replace />;
  return <>{children}</>;
}
