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
  const [fechaInput, setFechaInput] = useState(todayISO());
  const [busqueda, setBusqueda] = useState("");
  const [fechaConsulta, setFechaConsulta] = useState<string | null>(null);
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
    if (!fechaConsulta) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.historialPagos({
        fecha: fechaConsulta,
        page,
        page_size: 50,
        q: q || undefined,
      });
      setData(res);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "No se pudo cargar el historial.";
      setError(
        msg === "Not Found"
          ? "El servicio de historial no está disponible. Reinicie el servidor backend e intente de nuevo."
          : msg
      );
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [fechaConsulta, page, q]);

  useEffect(() => {
    load();
  }, [load]);

  const ejecutarBusqueda = (fecha: string, texto = busqueda) => {
    setPage(1);
    setQ(texto.trim());
    setFechaConsulta(fecha);
    setData(null);
    setError("");
  };

  const handleBuscar = (e: FormEvent) => {
    e.preventDefault();
    ejecutarBusqueda(fechaInput);
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
  const fechaMostrada = fechaConsulta ?? fechaInput;

  return (
    <>
      <div className="page-hero animate-fade-up">
        <div>
          <p className="hero-eyebrow">Consulta histórica</p>
          <h1 className="page-title">Historial de pagos</h1>
          <p className="page-subtitle hero-sub">
            El dashboard solo muestra el día actual. Aquí puede consultar cualquier fecha anterior.
          </p>
        </div>
      </div>

      <section className="historial-search-panel animate-fade-up animate-delay-1">
        <div className="historial-search-panel-head">
          <div>
            <h2>Buscar por fecha</h2>
            <p>Seleccione el día de operación y pulse consultar para ver todos los pagos.</p>
          </div>
          <span className="historial-search-panel-badge animate-badge-glow">Archivo histórico</span>
        </div>

        <form className="historial-search-panel-form" onSubmit={handleBuscar}>
          <div className="historial-search-fields">
            <label className="historial-field historial-field-date">
              <span>Fecha de operación</span>
              <input
                type="date"
                value={fechaInput}
                onChange={(e) => setFechaInput(e.target.value)}
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
                  setFechaInput(hoy);
                  ejecutarBusqueda(hoy);
                }}
              >
                Hoy
              </button>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => {
                  const ayer = offsetDateISO(-1);
                  setFechaInput(ayer);
                  ejecutarBusqueda(ayer);
                }}
              >
                Ayer
              </button>
            </div>
            <button type="submit" className="btn btn-primary btn-lg historial-search-btn animate-btn-shine">
              Consultar pagos
            </button>
          </div>
        </form>
      </section>

      {error && <div className="alert alert-error animate-shake">{error}</div>}

      {!fechaConsulta ? (
        <div className="card historial-empty-prompt animate-scale-in animate-delay-2">
          <p className="historial-empty-icon animate-icon-float" aria-hidden>
            ◷
          </p>
          <h3>Consulte un día del historial</h3>
          <p>
            Elija una fecha arriba y pulse <strong>Consultar pagos</strong> para ver los movimientos
            de ese día.
          </p>
        </div>
      ) : (
        <div key={`${fechaConsulta}-${q}`} className="historial-results animate-fade-up">
          <div className="cards-grid historial-summary animate-stagger">
            <div className="stat-card stat-card-accent">
              <div className="label">Total del día</div>
              <div className="value">{formatMoney(resumen?.importe_total ?? 0)}</div>
            </div>
            <div className="stat-card">
              <div className="label">Pagos encontrados</div>
              <div className="value">{resumen?.cantidad_pagos ?? 0}</div>
            </div>
            <div className="stat-card">
              <div className="label">Fecha consultada</div>
              <div className="value historial-fecha-value">{formatDate(fechaMostrada)}</div>
            </div>
          </div>

          <div className="card animate-fade-up animate-delay-2">
            <div className="card-header">
              <h2>Resultados — {formatDate(fechaMostrada)}</h2>
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
              <p className="empty-state animate-fade-up">No hay pagos registrados para esta fecha.</p>
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
