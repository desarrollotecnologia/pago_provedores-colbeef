import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../context/AuthContext";
import type { DashboardResponse, SmtpStatus } from "../types";
import { formatMoney } from "../utils/format";

export default function Dashboard() {
  const { config } = useAuth();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [smtp, setSmtp] = useState<SmtpStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [dash, smtpStatus] = await Promise.all([api.dashboard(), api.smtpStatus()]);
      setData(dash);
      setSmtp(smtpStatus);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) return <p className="page-subtitle">Cargando dashboard…</p>;

  const r = data?.resumen;

  return (
    <>
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">Resumen del período y actividad reciente</p>

      <div className="cards-grid">
        <div className="stat-card">
          <div className="label">Total pagado</div>
          <div className="value">{formatMoney(r?.importe_total ?? 0)}</div>
        </div>
        <div className="stat-card">
          <div className="label">Proveedores</div>
          <div className="value">{r?.cantidad_proveedores ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="label">Lotes</div>
          <div className="value">{r?.cantidad_lotes ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="label">Pagos</div>
          <div className="value">{r?.cantidad_pagos ?? 0}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Estado del sistema</h2>
          <div className="btn-group">
            <a href="/docs" target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">
              Abrir API
            </a>
            <button type="button" className="btn btn-primary btn-sm" onClick={load}>
              Actualizar
            </button>
          </div>
        </div>
        <p style={{ fontSize: "0.9rem", color: "var(--muted)" }}>
          API ok — {config?.env} — {config?.app_url}
        </p>
        {smtp && !smtp.configured && (
          <div className="alert alert-warn" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
            SMTP pendiente: configura SMTP_HOST y SMTP_PASSWORD en .env para enviar correos reales.
          </div>
        )}
      </div>

      <div className="two-cols">
        <div className="card">
          <div className="card-header">
            <h2>Top proveedores</h2>
            <Link to="/proveedores" className="btn btn-outline btn-sm">
              Ver todos
            </Link>
          </div>
          {data?.top_proveedores.length ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Proveedor</th>
                    <th>Total</th>
                    <th>Pagos</th>
                  </tr>
                </thead>
                <tbody>
                  {data.top_proveedores.slice(0, 8).map((p) => (
                    <tr key={p.proveedor_id}>
                      <td>{p.razon_social}</td>
                      <td className="money">{formatMoney(p.total_pagado)}</td>
                      <td>{p.cantidad_pagos}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="empty-state">Sin pagos registrados en el período.</p>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Lotes recientes</h2>
            <Link to="/pagos" className="btn btn-primary btn-sm">
              Nuevo lote
            </Link>
          </div>
          {data?.ultimos_lotes.length ? (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Concepto</th>
                    <th>Estado</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {data.ultimos_lotes.map((l) => (
                    <tr key={l.id}>
                      <td>
                        <Link to={`/pagos/${l.id}`}>#{l.id}</Link>
                      </td>
                      <td>{l.concepto_general}</td>
                      <td>
                        <StatusBadge estado={l.estado} />
                      </td>
                      <td className="money">{formatMoney(l.importe_total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="empty-state">No hay lotes creados todavía.</p>
          )}
        </div>
      </div>
    </>
  );
}
