import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, api } from "../api/client";
import { track } from "../telemetry/tracker";
import type { CambioProveedorDetalle, CambiosProveedorResponse } from "../types";
import {
  accionCambioClass,
  accionCambioLabel,
  formatDate,
  formatDateTime,
  offsetDateISO,
  todayISO,
} from "../utils/format";

export default function Cambios() {
  const hoy = todayISO();
  const [fechaDesde, setFechaDesde] = useState(hoy);
  const [fechaHasta, setFechaHasta] = useState(hoy);
  const [busqueda, setBusqueda] = useState("");
  const [rangoConsulta, setRangoConsulta] = useState<{ desde: string; hasta: string } | null>(null);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<CambiosProveedorResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detalle, setDetalle] = useState<CambioProveedorDetalle | null>(null);
  const [detalleLoading, setDetalleLoading] = useState(false);

  useEffect(() => {
    track("module_open", "cambios_proveedores", "Cambios en proveedores");
  }, []);

  const load = useCallback(async () => {
    if (!rangoConsulta) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.cambiosProveedores({
        fecha_desde: rangoConsulta.desde,
        fecha_hasta: rangoConsulta.hasta,
        page,
        page_size: 50,
        q: q || undefined,
      });
      setData(res);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "No se pudo cargar los cambios.";
      setError(
        msg.includes("Field required")
          ? "El servidor necesita actualizarse. Ejecute scripts\\update_server.bat y reinicie."
          : msg
      );
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [rangoConsulta, page, q]);

  useEffect(() => {
    load();
  }, [load]);

  const ejecutarBusqueda = (desde: string, hasta: string, texto = busqueda) => {
    if (hasta < desde) {
      setError("La fecha hasta no puede ser anterior a la fecha desde.");
      return;
    }
    setPage(1);
    setQ(texto.trim());
    setRangoConsulta({ desde, hasta });
    setData(null);
    setError("");
  };

  const handleBuscar = (e: FormEvent) => {
    e.preventDefault();
    ejecutarBusqueda(fechaDesde, fechaHasta);
  };

  const abrirDetalle = async (cambioId: number) => {
    setDetalleLoading(true);
    try {
      const d = await api.cambioProveedorDetalle(cambioId);
      setDetalle(d);
      track("action_complete", "cambios_proveedores", `Detalle cambio #${cambioId}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el detalle.");
    } finally {
      setDetalleLoading(false);
    }
  };

  const resumen = data?.resumen;
  const rangoLabel =
    rangoConsulta && rangoConsulta.desde === rangoConsulta.hasta
      ? formatDate(rangoConsulta.desde)
      : rangoConsulta
        ? `${formatDate(rangoConsulta.desde)} — ${formatDate(rangoConsulta.hasta)}`
        : "";

  return (
    <>
      <div className="page-hero animate-fade-up">
        <div>
          <p className="hero-eyebrow">Auditoría</p>
          <h1 className="page-title">Cambios en proveedores</h1>
          <p className="page-subtitle hero-sub">
            Registro de altas, ediciones y desactivaciones realizadas por los administradores.
          </p>
        </div>
      </div>

      <section className="historial-search-panel animate-fade-up animate-delay-1">
        <div className="historial-search-panel-head">
          <div>
            <h2>Buscar por período</h2>
            <p>Consulte qué cambios se hicieron en proveedores en el rango de fechas.</p>
          </div>
          <span className="historial-search-panel-badge animate-badge-glow">Registro de cambios</span>
        </div>

        <form className="historial-search-panel-form" onSubmit={handleBuscar}>
          <div className="historial-search-fields">
            <label className="historial-field historial-field-date">
              <span>Desde</span>
              <input
                type="date"
                value={fechaDesde}
                max={fechaHasta}
                onChange={(e) => setFechaDesde(e.target.value)}
                required
              />
            </label>

            <label className="historial-field historial-field-date">
              <span>Hasta</span>
              <input
                type="date"
                value={fechaHasta}
                min={fechaDesde}
                onChange={(e) => setFechaHasta(e.target.value)}
                required
              />
            </label>

            <label className="historial-field historial-field-text">
              <span>Proveedor o NIT</span>
              <input
                type="search"
                placeholder="Filtro opcional…"
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
              />
            </label>
          </div>

          <div className="historial-search-actions">
            <div className="historial-quick-dates">
              <span className="historial-quick-label">Acceso rápido</span>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => {
                  const h = todayISO();
                  setFechaDesde(h);
                  setFechaHasta(h);
                  ejecutarBusqueda(h, h);
                }}
              >
                Hoy
              </button>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => {
                  const fin = todayISO();
                  const inicio = offsetDateISO(-6);
                  setFechaDesde(inicio);
                  setFechaHasta(fin);
                  ejecutarBusqueda(inicio, fin);
                }}
              >
                7 días
              </button>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => {
                  const fin = todayISO();
                  const inicio = offsetDateISO(-29);
                  setFechaDesde(inicio);
                  setFechaHasta(fin);
                  ejecutarBusqueda(inicio, fin);
                }}
              >
                30 días
              </button>
            </div>
            <button type="submit" className="btn btn-primary btn-lg historial-search-btn animate-btn-shine">
              Consultar cambios
            </button>
          </div>
        </form>
      </section>

      {error && <div className="alert alert-error animate-shake">{error}</div>}

      {!rangoConsulta ? (
        <div className="card historial-empty-prompt animate-scale-in animate-delay-2">
          <p className="historial-empty-icon animate-icon-float" aria-hidden>
            ✎
          </p>
          <h3>Consulte un período de cambios</h3>
          <p>
            Elija <strong>desde</strong> y <strong>hasta</strong>, luego pulse{" "}
            <strong>Consultar cambios</strong>.
          </p>
        </div>
      ) : (
        <div key={`${rangoConsulta.desde}-${rangoConsulta.hasta}-${q}`} className="historial-results animate-fade-up">
          <div className="cards-grid historial-summary animate-stagger">
            <div className="stat-card stat-card-accent">
              <div className="label">Total del período</div>
              <div className="value">{resumen?.cantidad_cambios ?? 0}</div>
            </div>
            <div className="stat-card">
              <div className="label">Creaciones</div>
              <div className="value">{resumen?.creaciones ?? 0}</div>
            </div>
            <div className="stat-card">
              <div className="label">Ediciones</div>
              <div className="value">{resumen?.ediciones ?? 0}</div>
            </div>
            <div className="stat-card">
              <div className="label">Desactivaciones</div>
              <div className="value">{resumen?.desactivaciones ?? 0}</div>
            </div>
          </div>

          <div className="card animate-fade-up animate-delay-2">
            <div className="card-header">
              <h2>Resultados — {rangoLabel}</h2>
              {q && <span className="pill animate-scale-in">Filtro: {q}</span>}
            </div>

            {loading ? (
              <div className="historial-loading">
                <div className="historial-loading-bar" />
                <p>Cargando cambios…</p>
              </div>
            ) : data?.items.length ? (
              <>
                <div className="table-wrap table-animated">
                  <table>
                    <thead>
                      <tr>
                        <th>Fecha y hora</th>
                        <th>Acción</th>
                        <th>Proveedor</th>
                        <th>Identificación</th>
                        <th>Usuario</th>
                        <th>Resumen</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.items.map((item, i) => (
                        <tr
                          key={item.id}
                          className="animate-table-row"
                          style={{ animationDelay: `${0.04 + i * 0.045}s` }}
                        >
                          <td>{formatDateTime(item.registrado_en)}</td>
                          <td>
                            <span className={accionCambioClass(item.accion)}>
                              {accionCambioLabel(item.accion)}
                            </span>
                          </td>
                          <td>{item.razon_social}</td>
                          <td>{item.identificacion}</td>
                          <td>{item.usuario_nombre}</td>
                          <td>{item.resumen}</td>
                          <td>
                            <button
                              type="button"
                              className="btn btn-outline btn-sm"
                              onClick={() => abrirDetalle(item.id)}
                            >
                              Ver detalle
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {data.pages > 1 && (
                  <div className="pagination">
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      disabled={page <= 1}
                      onClick={() => setPage((p) => p - 1)}
                    >
                      Anterior
                    </button>
                    <span>
                      Página {data.page} de {data.pages}
                    </span>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      disabled={page >= data.pages}
                      onClick={() => setPage((p) => p + 1)}
                    >
                      Siguiente
                    </button>
                  </div>
                )}
              </>
            ) : (
              <p className="empty-state animate-fade-up">
                No hay cambios registrados en este período. Los movimientos nuevos aparecerán aquí
                al crear o editar proveedores.
              </p>
            )}
          </div>
        </div>
      )}

      {(detalle || detalleLoading) && (
        <div className="modal-overlay" onClick={() => !detalleLoading && setDetalle(null)}>
          <div className="modal historial-detalle-modal" onClick={(e) => e.stopPropagation()}>
            {detalleLoading || !detalle ? (
              <div className="pago-detalle-loading">
                <div className="historial-loading-bar" />
                <p>Cargando detalle…</p>
              </div>
            ) : (
              <>
                <header className="pago-detalle-header">
                  <div className="pago-detalle-header-main">
                    <p className="pago-detalle-eyebrow">Cambio #{detalle.id}</p>
                    <h3 className="pago-detalle-title">{detalle.razon_social}</h3>
                    <p className="pago-detalle-subtitle">
                      {formatDateTime(detalle.registrado_en)} · {detalle.usuario_nombre}
                    </p>
                  </div>
                  <div className="pago-detalle-header-side">
                    <span className={accionCambioClass(detalle.accion)}>
                      {accionCambioLabel(detalle.accion)}
                    </span>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm pago-detalle-close"
                      onClick={() => setDetalle(null)}
                    >
                      Cerrar
                    </button>
                  </div>
                </header>

                <div className="pago-detalle-body">
                  <p className="cambio-detalle-meta">
                    Proveedor #{detalle.proveedor_id} · NIT/ID {detalle.identificacion} ·{" "}
                    <Link to="/proveedores">Ir a proveedores</Link>
                  </p>

                  <div className="cambio-detalle-tabla-wrap">
                    <table className="cambio-detalle-tabla">
                      <thead>
                        <tr>
                          <th>Campo</th>
                          <th>Valor anterior</th>
                          <th>Valor nuevo</th>
                        </tr>
                      </thead>
                      <tbody>
                        {detalle.cambios.map((c) => (
                          <tr key={c.campo}>
                            <td>{c.etiqueta}</td>
                            <td>{c.anterior ?? "—"}</td>
                            <td>
                              <strong>{c.nuevo ?? "—"}</strong>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
