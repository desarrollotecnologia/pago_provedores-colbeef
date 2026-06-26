import { useCallback, useEffect, useState } from "react";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import { Bar, Doughnut, Line } from "react-chartjs-2";
import { api, ApiError } from "../api/client";
import { track } from "../telemetry/tracker";
import type { UsabilityStats } from "../types";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const CHART_COLORS = [
  "#1a6b42",
  "#2d9a63",
  "#145c38",
  "#4ade80",
  "#86efac",
  "#0c3d26",
  "#228552",
  "#5a7264",
];

const ACTION_LABELS: Record<string, string> = {
  session_start: "Inicio sesión",
  module_open: "Apertura módulo",
  action_complete: "Acción completada",
  error_ui: "Error visible",
  admin_open: "Dashboard usabilidad",
};

const MODULE_LABELS: Record<string, string> = {
  inicio: "Inicio",
  guia_uso: "Guía operador",
  dashboard_admin: "Dashboard admin",
  proveedores: "Proveedores",
  pagos: "Pagos",
  lote_detalle: "Detalle lote",
  configuracion: "Configuración",
  historial_pagos: "Historial",
  estadisticas_admin: "Estadísticas supervisor",
  usabilidad: "Usabilidad",
  auth: "Autenticación",
};

function labelAction(a: string) {
  return ACTION_LABELS[a] ?? a;
}

function labelModule(m: string) {
  return MODULE_LABELS[m] ?? m;
}

function formatTs(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("es-CO");
}

export default function UsabilidadDashboard() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<UsabilityStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const stats = await api.usabilityStats(days);
      setData(stats);
      track("module_open", "estadisticas_admin", `Consulta stats ${days} días`);
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? err.message
          : "No se pudieron cargar las estadísticas.";
      setError(
        `${msg} — Si es la primera vez, ejecute create_tables en el servidor para crear eventos_usabilidad.`
      );
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    load();
  }, [load]);

  const kpis = data?.kpis;
  const sinDatos = !loading && data && data.kpis.total_eventos === 0;

  const lineData = {
    labels: data?.eventos_por_dia.map((d) => d.dia) ?? [],
    datasets: [
      {
        label: "Eventos",
        data: data?.eventos_por_dia.map((d) => d.total) ?? [],
        borderColor: "#1a6b42",
        backgroundColor: "rgba(26,107,66,0.12)",
        fill: true,
        tension: 0.3,
      },
    ],
  };

  const usersData = {
    labels: data?.top_usuarios.map((u) => u.usuario) ?? [],
    datasets: [
      {
        label: "Eventos",
        data: data?.top_usuarios.map((u) => u.total) ?? [],
        backgroundColor: CHART_COLORS,
      },
    ],
  };

  const moduleData = {
    labels: data?.por_modulo.map((m) => labelModule(m.module)) ?? [],
    datasets: [
      {
        data: data?.por_modulo.map((m) => m.total) ?? [],
        backgroundColor: CHART_COLORS,
      },
    ],
  };

  const actionData = {
    labels: data?.por_accion.map((a) => labelAction(a.action)) ?? [],
    datasets: [
      {
        label: "Frecuencia",
        data: data?.por_accion.map((a) => a.total) ?? [],
        backgroundColor: "#1a6b42",
      },
    ],
  };

  const chartOpts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
  };

  return (
    <>
      <div className="page-hero">
        <div>
          <p className="hero-eyebrow">Supervisión de uso</p>
          <h1 className="page-title">Uso del administrador</h1>
          <p className="page-subtitle hero-sub">
            Frecuencia, módulos visitados y acciones del usuario administrador en el sistema
          </p>
        </div>
        <div className="btn-group">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              type="button"
              className={`btn btn-sm ${days === d ? "btn-primary" : "btn-outline"}`}
              onClick={() => setDays(d)}
            >
              {d} días
            </button>
          ))}
          <button type="button" className="btn btn-secondary btn-sm" onClick={load}>
            Actualizar
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {sinDatos && (
        <div className="alert alert-info">
          No hay actividad del administrador en los últimos {days} días. Los datos aparecerán
          cuando el usuario admin opere el sistema (pagos, proveedores, etc.).
        </div>
      )}

      <div className="cards-grid">
        <div className="stat-card">
          <div className="label">Total eventos</div>
          <div className="value">{kpis?.total_eventos ?? "—"}</div>
        </div>
        <div className="stat-card">
          <div className="label">Usuarios únicos</div>
          <div className="value">{kpis?.usuarios_unicos ?? "—"}</div>
        </div>
        <div className="stat-card">
          <div className="label">Sesiones únicas</div>
          <div className="value">{kpis?.sesiones_unicas ?? "—"}</div>
        </div>
        <div className="stat-card stat-card-accent">
          <div className="label">Última actividad</div>
          <div className="value" style={{ fontSize: "0.85rem", lineHeight: 1.4 }}>
            {kpis?.ultima_actividad?.usuario ? (
              <>
                <strong>{kpis.ultima_actividad.usuario}</strong>
                <br />
                {labelAction(kpis.ultima_actividad.action ?? "")} ·{" "}
                {labelModule(kpis.ultima_actividad.module ?? "")}
                <br />
                <span style={{ opacity: 0.85 }}>
                  {formatTs(kpis.ultima_actividad.timestamp)}
                </span>
              </>
            ) : (
              "—"
            )}
          </div>
        </div>
      </div>

      {loading ? (
        <p className="empty-state">Cargando estadísticas…</p>
      ) : data && data.kpis.total_eventos > 0 ? (
        <>
          <div className="two-cols">
            <div className="card chart-card">
              <div className="card-header">
                <h2>Tendencia — eventos por día</h2>
              </div>
              <div className="chart-container">
                <Line data={lineData} options={chartOpts} />
              </div>
            </div>
            <div className="card chart-card">
              <div className="card-header">
                <h2>Top usuarios activos</h2>
              </div>
              <div className="chart-container">
                <Bar
                  data={usersData}
                  options={{ ...chartOpts, indexAxis: "y" as const }}
                />
              </div>
            </div>
          </div>

          <div className="two-cols">
            <div className="card chart-card">
              <div className="card-header">
                <h2>Distribución por módulo</h2>
              </div>
              <div className="chart-container chart-container-sm">
                <Doughnut data={moduleData} options={{ responsive: true, maintainAspectRatio: false }} />
              </div>
            </div>
            <div className="card chart-card">
              <div className="card-header">
                <h2>Acciones más frecuentes</h2>
              </div>
              <div className="chart-container chart-container-sm">
                <Bar data={actionData} options={chartOpts} />
              </div>
            </div>
          </div>

          <div className="two-cols">
            <div className="card">
              <div className="card-header">
                <h2>Resumen por módulo</h2>
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Módulo</th>
                      <th>Visitas / eventos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.por_modulo.map((m) => (
                      <tr key={m.module}>
                        <td>{labelModule(m.module)}</td>
                        <td>{m.total}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2>Eventos recientes</h2>
              </div>
              <div className="table-wrap table-wrap-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Hora</th>
                      <th>Usuario</th>
                      <th>Acción</th>
                      <th>Módulo</th>
                      <th>Detalle</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.recientes.slice(0, 100).map((e, i) => (
                      <tr key={`${e.timestamp}-${i}`}>
                        <td>{formatTs(e.timestamp)}</td>
                        <td>{e.usuario}</td>
                        <td>{labelAction(e.action)}</td>
                        <td>{labelModule(e.module)}</td>
                        <td>{e.detail ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      ) : null}
    </>
  );
}
