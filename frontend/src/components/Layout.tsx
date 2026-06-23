import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV = [
  { to: "/", label: "Dashboard", icon: "📊" },
  { to: "/proveedores", label: "Proveedores", icon: "👥" },
  { to: "/pagos", label: "Pagos", icon: "💳" },
  { to: "/config", label: "Configuración", icon: "⚙️" },
];

export default function Layout() {
  const { user, config, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-logo">CB</div>
          <div>
            <h1>Pago Proveedores</h1>
            <p>Colbeef</p>
          </div>
        </div>
        <nav className="sidebar-nav">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">v{config?.version ?? "1.0"}</div>
      </aside>

      <div className="main-content">
        <header className="topbar">
          <div>
            <strong>{config?.app_name ?? "Pago Proveedores"}</strong>
          </div>
          <div className="topbar-user">
            <span className="badge">
              {user?.nombre_completo ?? user?.username} ({user?.rol})
            </span>
            <button type="button" className="btn btn-primary btn-sm" onClick={handleLogout}>
              Salir
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
