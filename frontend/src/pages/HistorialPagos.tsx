import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, api } from "../api/client";
import StatusBadge from "../components/StatusBadge";
import { track } from "../telemetry/tracker";
import type { CatalogoItem, HistorialPagoDetalle, HistorialPagosResponse } from "../types";
import { formatDate, formatMoney, offsetDateISO, todayISO } from "../utils/format";
import { TIPOS_IDENTIFICACION_NIT } from "../utils/nit";

function isEmptyValue(value: React.ReactNode): boolean {
  if (value == null) return true;
  if (typeof value === "string") {
    const t = value.trim();
    return t === "" || t === "—";
  }
  return false;
}

function DetailField({
  label,
  value,
  mono,
}: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}) {
  if (isEmptyValue(value)) return null;
  return (
    <div className="pago-detalle-field">
      <dt className="pago-detalle-field-label">{label}</dt>
      <dd className={`pago-detalle-field-value${mono ? " pago-detalle-mono" : ""}`}>{value}</dd>
    </div>
  );
}

function DetailCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <article className="pago-detalle-card">
      <h4 className="pago-detalle-card-title">{title}</h4>
      <dl className="pago-detalle-dl">{children}</dl>
    </article>
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
          ? "El historial requiere reiniciar el servidor. Ejecute scripts\\restart.bat y vuelva a consultar."
          : msg.includes("Field required")
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
                    <p className="pago-detalle-eyebrow">Pago #{detalle.id}</p>
                    <h3 className="pago-detalle-title">{detalle.razon_social}</h3>
                    <p className="pago-detalle-subtitle">
                      {TIPOS_IDENTIFICACION_NIT.has(detalle.tipo_identificacion) &&
                      detalle.digito_verificacion != null
                        ? `NIT ${detalle.identificacion}-${detalle.digito_verificacion}`
                        : `${labelTipo(detalle.tipo_identificacion, tiposId)} ${detalle.identificacion}`}
                    </p>
                  </div>
                  <div className="pago-detalle-header-side">
                    <div className="pago-detalle-importe">{formatMoney(detalle.importe)}</div>
                    <StatusBadge estado={detalle.estado} />
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
                  <div className="pago-detalle-cards">
                    <DetailCard title="Información del pago">
                      <DetailField label="Factura" value={detalle.numero_factura} />
                      <DetailField label="Concepto principal" value={detalle.concepto1} />
                      <DetailField label="Concepto 2" value={detalle.concepto2} />
                      <DetailField label="Concepto 3" value={detalle.concepto3} />
                      <DetailField label="Concepto 4" value={detalle.concepto4} />
                      <DetailField
                        label="Fecha límite"
                        value={detalle.fecha_limite ? formatDate(detalle.fecha_limite) : null}
                      />
                      <DetailField label="Correo destino" value={detalle.email_destino} />
                    </DetailCard>

                    <DetailCard title="Cuenta destino">
                      <DetailField
                        label="Banco"
                        value={
                          detalle.banco_descripcion
                            ? `${detalle.banco_codigo} — ${detalle.banco_descripcion}`
                            : String(detalle.banco_codigo)
                        }
                      />
                      <DetailField
                        label="Tipo de cuenta"
                        value={labelTipo(detalle.tipo_cuenta, tiposCuenta)}
                      />
                      <DetailField label="Número de cuenta" value={detalle.numero_cuenta} mono />
                      <DetailField label="Código oficina" value={detalle.cod_oficina} />
                      <DetailField label="Forma de pago" value={String(detalle.forma_pago)} />
                    </DetailCard>

                    <DetailCard title="Lote asociado">
                      <DetailField
                        label="Número de lote"
                        value={<Link to={`/pagos/${detalle.lote_id}`}>#{detalle.lote_id}</Link>}
                      />
                      <DetailField
                        label="Fecha de operación"
                        value={formatDate(detalle.lote_fecha_operacion)}
                      />
                      <DetailField label="Concepto del lote" value={detalle.lote_concepto} />
                      <DetailField
                        label="Estado del lote"
                        value={<StatusBadge estado={detalle.lote_estado} />}
                      />
                      <DetailField
                        label="Total del lote"
                        value={formatMoney(detalle.lote_importe_total)}
                      />
                      <DetailField label="Archivo plano" value={detalle.lote_archivo} mono />
                    </DetailCard>
                  </div>

                  {(detalle.referencia_16 || detalle.referencia_11) && (
                    <aside className="pago-detalle-refs">
                      <p className="pago-detalle-refs-title">Referencias del archivo bancario</p>
                      <div className="pago-detalle-refs-grid">
                        {detalle.referencia_16 && (
                          <div>
                            <span>Referencia 16</span>
                            <code>{detalle.referencia_16}</code>
                          </div>
                        )}
                        {detalle.referencia_11 && (
                          <div>
                            <span>Referencia 11</span>
                            <code>{detalle.referencia_11}</code>
                          </div>
                        )}
                      </div>
                    </aside>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
