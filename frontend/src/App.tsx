import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import Config from "./pages/Config";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import LoteDetail from "./pages/LoteDetail";
import Pagos from "./pages/Pagos";
import Proveedores from "./pages/Proveedores";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="login-page">Cargando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="proveedores" element={<Proveedores />} />
        <Route path="pagos" element={<Pagos />} />
        <Route path="pagos/:id" element={<LoteDetail />} />
        <Route path="config" element={<Config />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
