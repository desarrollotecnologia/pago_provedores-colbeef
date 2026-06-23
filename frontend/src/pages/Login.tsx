import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";
import { ApiError } from "../api/client";
import BrandLogoBox from "../components/BrandLogoBox";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { user, loading, login } = useAuth();
  const [usuario, setUsuario] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) return <Navigate to="/" replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(usuario.trim(), password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Credenciales incorrectas");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-bg-pattern" />
      <div className="login-container">
        <div className="login-brand">
          <BrandLogoBox />
          <div>
            <h1>Pago Proveedores</h1>
            <p>Colbeef · Sistema interno de tesorería</p>
          </div>
        </div>

        <div className="login-card">
          <div className="login-card-header">
            <h2>Acceso seguro</h2>
            <p>Ingrese sus credenciales corporativas</p>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
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
            <div className="form-group">
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
            <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
              {submitting ? "Verificando…" : "Iniciar sesión"}
            </button>
          </form>

          <p className="login-security-note">
            La sesión es privada por navegador. Compartir un enlace no da acceso sin credenciales.
          </p>
        </div>
      </div>
    </div>
  );
}
