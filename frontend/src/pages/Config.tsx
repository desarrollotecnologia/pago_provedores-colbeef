import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { SmtpStatus } from "../types";

export default function Config() {
  const { config } = useAuth();
  const [smtp, setSmtp] = useState<SmtpStatus | null>(null);

  useEffect(() => {
    api.smtpStatus().then(setSmtp);
  }, []);

  return (
    <>
      <h1 className="page-title">Configuración</h1>
      <p className="page-subtitle">Parámetros del sistema (se editan en el archivo .env del servidor)</p>

      <div className="card">
        <div className="card-header">
          <h2>Aplicación</h2>
        </div>
        <div className="form-grid">
          <div className="form-group">
            <label>Nombre</label>
            <input value={config?.app_name ?? ""} readOnly />
          </div>
          <div className="form-group">
            <label>URL pública</label>
            <input value={config?.app_url ?? ""} readOnly />
          </div>
          <div className="form-group">
            <label>Entorno</label>
            <input value={config?.env ?? ""} readOnly />
          </div>
          <div className="form-group">
            <label>Versión API</label>
            <input value={config?.version ?? ""} readOnly />
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Correo SMTP</h2>
        </div>
        {smtp && !smtp.configured ? (
          <div className="alert alert-warn">
            SMTP no configurado. Edita en el servidor el archivo <code>.env</code>:
            <pre style={{ marginTop: "0.5rem", fontSize: "0.8rem" }}>
              {`SMTP_HOST=servidor-correo.colbeef.com\nSMTP_PASSWORD=tu-contraseña\nSMTP_USER=coordinacion.tesoreria@colbeef.com`}
            </pre>
            Luego ejecuta <code>scripts\\restart.bat</code>
          </div>
        ) : (
          <div className="alert alert-success">
            SMTP configurado — host: {smtp?.host} — remitente: {smtp?.from_email}
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Flujo operativo (viernes)</h2>
        </div>
        <ol style={{ paddingLeft: "1.25rem", lineHeight: 2, fontSize: "0.9rem", color: "var(--muted)" }}>
          <li>
            Ir a <strong>Pagos</strong> → <strong>Nuevo lote</strong>
          </li>
          <li>Agregar proveedores e importes al lote</li>
          <li>
            <strong>Generar archivo</strong> → descargar TXT para el banco
          </li>
          <li>
            <strong>Enviar correos</strong> o <strong>Procesar todo</strong> (archivo + correos)
          </li>
        </ol>
      </div>
    </>
  );
}
