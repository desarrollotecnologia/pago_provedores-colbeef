import { NavLink, Outlet, useNavigate } from "react-router-dom";
import BrandLogoBox from "./BrandLogoBox";
import { useAuth } from "../context/AuthContext";
import { useRole } from "../hooks/useRole";
import { usePageTracking } from "../telemetry/usePageTracking";

const ADMIN_NAV = [
  { to: "/", label: "Dashboard", icon: "◈" },
  { to: "/proveedores", label: "Proveedores", icon: "◎" },
  { to: "/pagos", label: "Pagos", icon: "◆" },
  { to: "/config", label: "Configuración", icon: "◇" },
];

export default function Layout() {
  const { user, config, logout } = useAuth();
  const { isAdmin } = useRole();
  const navigate = useNavigate();
  usePageTracking();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className={`app-shell${isAdmin ? "" : " app-shell-operador"}`}>
      <aside className="sidebar">
        <div className="sidebar-brand">
          <BrandLogoBox size="sm" />
          <div>
            <h1>Pago Proveedores</h1>
            <p>Colbeef · Tesorería</p>
          </div>
        </div>

        <div className="sidebar-role">
          {isAdmin ? "Administrador — operaciones" : "Supervisor — estadísticas de uso"}
        </div>

        {isAdmin ? (
          <nav className="sidebar-nav">
            {ADMIN_NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </nav>
        ) : (
          <div className="sidebar-operador-note">
            <p>
              Monitoreo del uso del sistema por el administrador: frecuencia, módulos y acciones.
            </p>
          </div>
        )}

        <div className="sidebar-footer">
          <div>v{config?.version ?? "1.0"}</div>
          <div className="sidebar-footer-muted">Uso interno Colbeef</div>
        </div>
      </aside>

      <div className="main-content">
        <header className="topbar">
          <div className="topbar-title">
            <span className="topbar-label">
              {isAdmin ? "Sistema de pagos" : "Telemetría de usabilidad"}
            </span>
            <strong>{config?.app_name ?? "Pago Proveedores"}</strong>
          </div>
          <div className="topbar-user">
            <div className="user-chip">
              <span className="user-avatar">{(user?.nombre_completo ?? "U")[0]}</span>
              <div>
                <div className="user-name">{user?.nombre_completo ?? user?.username}</div>
                <div className="user-role">{isAdmin ? "Administrador" : "Supervisor"}</div>
              </div>
            </div>
            <button type="button" className="btn btn-ghost btn-sm" onClick={handleLogout}>
              Cerrar sesión
            </button>
          </div>
        </header>
        <main className="page">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
