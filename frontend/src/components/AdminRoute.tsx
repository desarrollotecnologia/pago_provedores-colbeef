import { Navigate } from "react-router-dom";
import { useRole } from "../hooks/useRole";

export default function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAdmin } = useRole();
  if (!isAdmin) return <Navigate to="/" replace />;
  return <>{children}</>;
}
