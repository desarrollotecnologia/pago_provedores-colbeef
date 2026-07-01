import { FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { user, loading, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string })?.from ?? "/";

  const [usuario, setUsuario] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) {
    return <Navigate to={from} replace />;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(usuario.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Credenciales incorrectas");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-bg-pattern" />
      <div className="login-split">
        <aside className="login-panel-brand">
          <div className="login-colbeef-logo-wrap">
            <div className="login-colbeef-logo-card">
              <img
                src="/colbeef-logo.png"
                alt="Colbeef"
                className="login-colbeef-logo"
                width={220}
                height={56}
              />
            </div>
          </div>
          <h1>Pago Proveedores</h1>
          <p>Colbeef · Sistema interno de tesorería</p>
          <ul className="login-features">
            <li>Gestión de lotes y pagos a proveedores</li>
            <li>Generación de archivo plano bancario</li>
            <li>Envío automático de soportes por correo</li>
          </ul>
        </aside>

        <div className="login-panel-form">
          <div className="login-card">
            <div className="login-card-header">
              <h2>Acceso seguro</h2>
              <p>Ingrese sus credenciales corporativas</p>
            </div>

            {error && <div className="alert alert-error login-error-shake">{error}</div>}

            <form onSubmit={handleSubmit}>
              <div className="form-group login-field-anim" style={{ animationDelay: "0.35s" }}>
                <label htmlFor="usuario">Usuario</label>
                <input
                  id="usuario"
                  value={usuario}
                  onChange={(e) => setUsuario(e.target.value)}
                  autoComplete="username"
                  placeholder="Su usuario asignado"
                  required
                />
              </div>
              <div className="form-group login-field-anim" style={{ animationDelay: "0.42s" }}>
                <label htmlFor="password">Contraseña</label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  required
                />
              </div>
              <button
                type="submit"
                className={`btn btn-primary btn-block btn-lg login-field-anim${submitting ? " btn-loading" : ""}`}
                style={{ animationDelay: "0.5s" }}
                disabled={submitting}
              >
                {submitting ? "Verificando…" : "Iniciar sesión"}
              </button>
            </form>

          <p className="login-security-note">
            La sesión solo dura mientras esta pestaña está abierta. Al recargar o abrir el enlace en
            otra pestaña deberá iniciar sesión de nuevo.
          </p>
          </div>
        </div>
      </div>
    </div>
  );
}
