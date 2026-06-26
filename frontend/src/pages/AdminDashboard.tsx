import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../context/AuthContext";
import { track } from "../telemetry/tracker";
import type { DashboardResponse } from "../types";
import { formatMoney, isSameDayISO, todayISO } from "../utils/format";

export default function AdminDashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const hoy = todayISO();

  useEffect(() => {
    track("module_open", "dashboard_admin", "Dashboard ejecutivo");
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const dash = await api.dashboard({ fecha_desde: hoy, fecha_hasta: hoy });
      setData(dash);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "No se pudo cargar el dashboard administrativo.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [hoy]);

  useEffect(() => {
    load();
  }, [load]);

  const r = data?.resumen;

  const lotesHoy = useMemo(
    () => data?.ultimos_lotes.filter((l) => isSameDayISO(l.fecha_operacion, hoy)) ?? [],
    [data?.ultimos_lotes, hoy]
  );

  const proveedoresHoy = useMemo(() => {
    if (!r || (r.cantidad_pagos ?? 0) === 0) return [];
    return data?.top_proveedores ?? [];
  }, [data?.top_proveedores, r]);

  const sinActividadHoy =
    !loading &&
    (r?.cantidad_pagos ?? 0) === 0 &&
    (r?.cantidad_lotes ?? 0) === 0 &&
    lotesHoy.length === 0;

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="skeleton skeleton-welcome animate-pulse-soft" />
        <div className="skeleton skeleton-title animate-pulse-soft animate-delay-1" />
        <div className="cards-grid">
          {[0, 1, 2, 3].map((i) => (
            <div
              key={i}
              className="skeleton skeleton-stat animate-pulse-soft"
              style={{ animationDelay: `${0.1 + i * 0.08}s` }}
            />
          ))}
        </div>
      </div>
    );
  }

  const primerNombre = user?.nombre_completo?.split(" ")[0] ?? user?.username ?? "Usuario";
  const fechaHoy = new Date().toLocaleDateString("es-CO", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  return (
    <>
      <div className="dashboard-welcome animate-fade-up">
        <div>
          <h2>Hola, {primerNombre}</h2>
          <p>{fechaHoy}</p>
        </div>
        <span className="dashboard-welcome-badge">Tesorería Colbeef</span>
      </div>

      <div className="page-hero animate-fade-up animate-delay-1">
        <div>
          <p className="hero-eyebrow">Administración</p>
          <h1 className="page-title">Dashboard ejecutivo</h1>
          <p className="page-subtitle hero-sub">
            Solo actividad de hoy — el historial conserva los días anteriores
          </p>
        </div>
        <button type="button" className="btn btn-secondary" onClick={load}>
          Actualizar
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {sinActividadHoy && (
        <div className="alert alert-info dashboard-day-empty animate-scale-in">
          Hoy aún no hay pagos ni lotes registrados. Los días anteriores están disponibles en{" "}
          <Link to="/historial">Historial</Link>.
        </div>
      )}

      <div className="cards-grid animate-stagger">
        <div className="stat-card stat-card-accent">
          <div className="stat-card-header">
            <div>
              <div className="label">Total pagado hoy</div>
              <div className="value">{formatMoney(r?.importe_total ?? 0)}</div>
            </div>
            <span className="stat-card-icon" aria-hidden>
              $
            </span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <div>
              <div className="label">Proveedores hoy</div>
              <div className="value">{r?.cantidad_proveedores ?? 0}</div>
            </div>
            <span className="stat-card-icon" aria-hidden>
              ◎
            </span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <div>
              <div className="label">Lotes de hoy</div>
              <div className="value">{r?.cantidad_lotes ?? 0}</div>
            </div>
            <span className="stat-card-icon" aria-hidden>
              ◫
            </span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <div>
              <div className="label">Pagos de hoy</div>
              <div className="value">{r?.cantidad_pagos ?? 0}</div>
            </div>
            <span className="stat-card-icon" aria-hidden>
              ⇄
            </span>
          </div>
        </div>
      </div>

      <div className="two-cols animate-fade-up animate-delay-3">
        <div className="card">
          <div className="card-header">
            <h2>Top proveedores hoy</h2>
            <Link to="/proveedores" className="btn btn-outline btn-sm">
              Ver todos
            </Link>
          </div>
          {proveedoresHoy.length ? (
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
                  {proveedoresHoy.slice(0, 8).map((p) => (
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
            <p className="empty-state">Sin pagos hoy.</p>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Lotes de hoy</h2>
            <div className="card-header-actions">
              <Link to="/historial" className="btn btn-outline btn-sm">
                Historial
              </Link>
              <Link to="/pagos" className="btn btn-primary btn-sm">
                Nuevo lote
              </Link>
            </div>
          </div>
          {lotesHoy.length ? (
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
                  {lotesHoy.map((l) => (
                    <tr key={l.id}>
                      <td>
                        <Link to={`/pagos/${l.id}`}>#{l.id}</Link>
                      </td>
                      <td>{l.concepto_general ?? l.concepto ?? "Sin concepto"}</td>
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
            <p className="empty-state">No hay lotes registrados hoy.</p>
          )}
        </div>
      </div>
    </>
  );
}
