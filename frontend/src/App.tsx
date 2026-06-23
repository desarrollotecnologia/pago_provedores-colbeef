import { Navigate, Route, Routes } from "react-router-dom";
import AdminRoute from "./components/AdminRoute";
import Layout from "./components/Layout";
import { useAuth } from "./context/AuthContext";
import { useRole } from "./hooks/useRole";
import AdminDashboard from "./pages/AdminDashboard";
import Config from "./pages/Config";
import Login from "./pages/Login";
import LoteDetail from "./pages/LoteDetail";
import OperadorDashboard from "./pages/OperadorDashboard";
import Pagos from "./pages/Pagos";
import Proveedores from "./pages/Proveedores";
import UsabilidadDashboard from "./pages/UsabilidadDashboard";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading-screen">Cargando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function HomePage() {
  const { isAdmin } = useRole();
  return isAdmin ? <AdminDashboard /> : <OperadorDashboard />;
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
        <Route index element={<HomePage />} />
        <Route
          path="proveedores"
          element={
            <AdminRoute>
              <Proveedores />
            </AdminRoute>
          }
        />
        <Route
          path="pagos"
          element={
            <AdminRoute>
              <Pagos />
            </AdminRoute>
          }
        />
        <Route
          path="pagos/:id"
          element={
            <AdminRoute>
              <LoteDetail />
            </AdminRoute>
          }
        />
        <Route
          path="config"
          element={
            <AdminRoute>
              <Config />
            </AdminRoute>
          }
        />
        <Route
          path="usabilidad"
          element={
            <AdminRoute>
              <UsabilidadDashboard />
            </AdminRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
