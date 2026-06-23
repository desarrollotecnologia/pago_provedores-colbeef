import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useRole } from "../hooks/useRole";
import { bindUsabilityShortcut } from "../telemetry/tracker";
import { usePageTracking } from "../telemetry/usePageTracking";

const ADMIN_NAV = [
  { to: "/", label: "Dashboard", icon: "◈" },
  { to: "/proveedores", label: "Proveedores", icon: "◎" },
  { to: "/pagos", label: "Pagos", icon: "◆" },
  { to: "/config", label: "Configuración", icon: "◇" },
  { to: "/usabilidad", label: "Usabilidad", icon: "◉", discreet: true },
];

export default function Layout() {
  const { user, config, logout } = useAuth();
  const { isAdmin } = useRole();
  const navigate = useNavigate();
  usePageTracking();

  useEffect(() => {
    if (!isAdmin) return;
    return bindUsabilityShortcut(() => navigate("/usabilidad"));
  }, [isAdmin, navigate]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className={`app-shell${isAdmin ? "" : " app-shell-operador"}`}>
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-logo">CB</div>
          <div>
            <h1>Pago Proveedores</h1>
            <p>Colbeef · Tesorería</p>
          </div>
        </div>

        <div className="sidebar-role">
          {isAdmin ? "Administrador — operaciones" : "Operador — guía de uso"}
        </div>

        {isAdmin && (
          <nav className="sidebar-nav">
            {ADMIN_NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  `nav-link${isActive ? " active" : ""}${"discreet" in item && item.discreet ? " nav-link-discreet" : ""}`
                }
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </nav>
        )}

        {!isAdmin && (
          <div className="sidebar-operador-note">
            <p>Consulte aquí cómo funciona el sistema. No tiene permisos para operar pagos.</p>
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
              {isAdmin ? "Sistema de pagos" : "Guía de usabilidad"}
            </span>
            <strong>{config?.app_name ?? "Pago Proveedores"}</strong>
          </div>
          <div className="topbar-user">
            <div className="user-chip">
              <span className="user-avatar">{(user?.nombre_completo ?? "U")[0]}</span>
              <div>
                <div className="user-name">{user?.nombre_completo ?? user?.username}</div>
                <div className="user-role">{isAdmin ? "Administrador" : "Operador"}</div>
              </div>
            </div>
            <span className="telemetry-badge" title="Sesión activa — telemetría anónima de uso">
              {user?.username}
            </span>
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
