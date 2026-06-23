import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import AdminRoute from "./components/AdminRoute";
import Layout from "./components/Layout";
import { useAuth } from "./context/AuthContext";
import { useRole } from "./hooks/useRole";
import AdminDashboard from "./pages/AdminDashboard";
import Login from "./pages/Login";
import LoteDetail from "./pages/LoteDetail";
import Pagos from "./pages/Pagos";
import Proveedores from "./pages/Proveedores";
import UsabilidadDashboard from "./pages/UsabilidadDashboard";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <div className="loading-screen">Verificando sesión…</div>;
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <>{children}</>;
}

function HomePage() {
  const { isAdmin, isOperador } = useRole();
  if (isOperador) return <UsabilidadDashboard />;
  if (isAdmin) return <AdminDashboard />;
  return <Navigate to="/login" replace />;
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
        <Route path="config" element={<Navigate to="/" replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
