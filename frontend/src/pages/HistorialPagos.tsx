import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, api } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import { track } from "../telemetry/tracker";
import type { CatalogoItem, HistorialPagoDetalle, HistorialPagosResponse } from "../types";
import { formatDate, formatMoney, offsetDateISO, todayISO } from "../utils/format";

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="detail-row">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{value ?? "—"}</span>
    </div>
  );
}

export default function HistorialPagos() {
  const hoy = todayISO();
  const [fechaDesde, setFechaDesde] = useState(hoy);
  const [fechaHasta, setFechaHasta] = useState(hoy);
  const [busqueda, setBusqueda] = useState("");
  const [rangoConsulta, setRangoConsulta] = useState<{ desde: string; hasta: string } | null>(null);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<HistorialPagosResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detalle, setDetalle] = useState<HistorialPagoDetalle | null>(null);
  const [detalleLoading, setDetalleLoading] = useState(false);
  const [tiposId, setTiposId] = useState<CatalogoItem[]>([]);
  const [tiposCuenta, setTiposCuenta] = useState<CatalogoItem[]>([]);

  useEffect(() => {
    track("module_open", "historial_pagos", "Historial de pagos");
    Promise.all([api.tiposIdentificacion(), api.tiposCuenta()]).then(([id, cuenta]) => {
      setTiposId(id);
      setTiposCuenta(cuenta);
    });
  }, []);

  const load = useCallback(async () => {
    if (!rangoConsulta) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.historialPagos({
        fecha_desde: rangoConsulta.desde,
        fecha_hasta: rangoConsulta.hasta,
        page,
        page_size: 50,
        q: q || undefined,
      });
      setData(res);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "No se pudo cargar el historial.";
      setError(
        msg === "Not Found" || msg === "Historial no disponible"
          ? "El historial requiere reiniciar el servidor. Ejecute scripts\\start.bat y vuelva a consultar."
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

  const abrirDetalle = async (pagoId: number) => {
    setDetalleLoading(true);
    try {
      const d = await api.historialPagoDetalle(pagoId);
      setDetalle(d);
      track("action_complete", "historial_pagos", `Detalle pago #${pagoId}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el detalle.");
    } finally {
      setDetalleLoading(false);
    }
  };

  const labelTipo = (codigo: number, lista: CatalogoItem[]) =>
    lista.find((t) => t.codigo === codigo)?.descripcion ?? String(codigo);

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
          <p className="hero-eyebrow">Consulta histórica</p>
          <h1 className="page-title">Historial de pagos</h1>
          <p className="page-subtitle hero-sub">
            El dashboard solo muestra el día actual. Aquí puede consultar un rango de fechas.
          </p>
        </div>
      </div>

      <section className="historial-search-panel animate-fade-up animate-delay-1">
        <div className="historial-search-panel-head">
          <div>
            <h2>Buscar por período</h2>
            <p>Defina desde y hasta para ver todos los pagos del rango seleccionado.</p>
          </div>
          <span className="historial-search-panel-badge animate-badge-glow">Archivo histórico</span>
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
              <span>Proveedor, NIT o factura</span>
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
                  const hoy = todayISO();
                  setFechaDesde(hoy);
                  setFechaHasta(hoy);
                  ejecutarBusqueda(hoy, hoy);
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
              Consultar pagos
            </button>
          </div>
        </form>
      </section>

      {error && <div className="alert alert-error animate-shake">{error}</div>}

      {!rangoConsulta ? (
        <div className="card historial-empty-prompt animate-scale-in animate-delay-2">
          <p className="historial-empty-icon animate-icon-float" aria-hidden>
            ◷
          </p>
          <h3>Consulte un período del historial</h3>
          <p>
            Elija <strong>desde</strong> y <strong>hasta</strong>, luego pulse{" "}
            <strong>Consultar pagos</strong>.
          </p>
        </div>
      ) : (
        <div key={`${rangoConsulta.desde}-${rangoConsulta.hasta}-${q}`} className="historial-results animate-fade-up">
          <div className="cards-grid historial-summary animate-stagger">
            <div className="stat-card stat-card-accent">
              <div className="label">Total del período</div>
              <div className="value">{formatMoney(resumen?.importe_total ?? 0)}</div>
            </div>
            <div className="stat-card">
              <div className="label">Pagos encontrados</div>
              <div className="value">{resumen?.cantidad_pagos ?? 0}</div>
            </div>
            <div className="stat-card">
              <div className="label">Período</div>
              <div className="value historial-fecha-value">{rangoLabel}</div>
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
                <p>Cargando pagos…</p>
              </div>
            ) : data?.items.length ? (
              <>
                <div className="table-wrap table-animated">
                  <table>
                    <thead>
                      <tr>
                        <th>Lote</th>
                        <th>Proveedor</th>
                        <th>Identificación</th>
                        <th>Factura</th>
                        <th>Concepto</th>
                        <th>Estado</th>
                        <th>Importe</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.items.map((p, i) => (
                        <tr
                          key={p.id}
                          className="animate-table-row"
                          style={{ animationDelay: `${0.04 + i * 0.045}s` }}
                        >
                          <td>
                            <Link to={`/pagos/${p.lote_id}`}>#{p.lote_id}</Link>
                          </td>
                          <td>{p.razon_social}</td>
                          <td>{p.identificacion}</td>
                          <td>{p.numero_factura ?? "—"}</td>
                          <td>{p.concepto1 ?? p.lote_concepto}</td>
                          <td>
                            <StatusBadge estado={p.estado} />
                          </td>
                          <td className="money">{formatMoney(p.importe)}</td>
                          <td>
                            <button
                              type="button"
                              className="btn btn-outline btn-sm"
                              onClick={() => abrirDetalle(p.id)}
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
              <p className="empty-state animate-fade-up">No hay pagos registrados en este período.</p>
            )}
          </div>
        </div>
      )}

      {(detalle || detalleLoading) && (
        <div className="modal-overlay" onClick={() => !detalleLoading && setDetalle(null)}>
          <div className="modal modal-wide historial-detalle-modal" onClick={(e) => e.stopPropagation()}>
            {detalleLoading || !detalle ? (
              <p>Cargando detalle…</p>
            ) : (
              <>
                <div className="card-header">
                  <h3>Detalle del pago #{detalle.id}</h3>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => setDetalle(null)}>
                    Cerrar
                  </button>
                </div>

                <div className="historial-detalle-grid">
                  <section>
                    <h4>Proveedor</h4>
                    <DetailRow label="Razón social" value={detalle.razon_social} />
                    <DetailRow
                      label="Identificación"
                      value={
                        detalle.tipo_identificacion === 3 && detalle.digito_verificacion != null
                          ? `${detalle.identificacion}-${detalle.digito_verificacion}`
                          : detalle.identificacion
                      }
                    />
                    <DetailRow
                      label="Tipo ID"
                      value={labelTipo(detalle.tipo_identificacion, tiposId)}
                    />
                    <DetailRow label="Email" value={detalle.email_destino} />
                  </section>

                  <section>
                    <h4>Pago</h4>
                    <DetailRow label="Importe" value={formatMoney(detalle.importe)} />
                    <DetailRow label="Factura" value={detalle.numero_factura} />
                    <DetailRow label="Concepto 1" value={detalle.concepto1} />
                    <DetailRow label="Concepto 2" value={detalle.concepto2} />
                    <DetailRow label="Concepto 3" value={detalle.concepto3} />
                    <DetailRow label="Concepto 4" value={detalle.concepto4} />
                    <DetailRow label="Estado" value={<StatusBadge estado={detalle.estado} />} />
                    <DetailRow label="Ref. 16" value={detalle.referencia_16} />
                    <DetailRow label="Ref. 11" value={detalle.referencia_11} />
                  </section>

                  <section>
                    <h4>Cuenta destino</h4>
                    <DetailRow
                      label="Banco"
                      value={
                        detalle.banco_descripcion
                          ? `${detalle.banco_codigo} — ${detalle.banco_descripcion}`
                          : detalle.banco_codigo
                      }
                    />
                    <DetailRow
                      label="Tipo cuenta"
                      value={labelTipo(detalle.tipo_cuenta, tiposCuenta)}
                    />
                    <DetailRow label="Número cuenta" value={detalle.numero_cuenta} />
                    <DetailRow label="Cód. oficina" value={detalle.cod_oficina} />
                    <DetailRow label="Forma pago" value={detalle.forma_pago} />
                    <DetailRow label="Fecha límite" value={formatDate(detalle.fecha_limite)} />
                  </section>

                  <section>
                    <h4>Lote</h4>
                    <DetailRow
                      label="Lote"
                      value={<Link to={`/pagos/${detalle.lote_id}`}>#{detalle.lote_id}</Link>}
                    />
                    <DetailRow label="Fecha operación" value={formatDate(detalle.lote_fecha_operacion)} />
                    <DetailRow label="Concepto lote" value={detalle.lote_concepto} />
                    <DetailRow label="Estado lote" value={<StatusBadge estado={detalle.lote_estado} />} />
                    <DetailRow label="Total lote" value={formatMoney(detalle.lote_importe_total)} />
                    <DetailRow label="Archivo plano" value={detalle.lote_archivo} />
                  </section>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
