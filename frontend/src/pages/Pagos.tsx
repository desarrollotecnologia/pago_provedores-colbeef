import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError, api } from "../api/client";
import { trackAction } from "../telemetry/tracker";
import InfoLote from "../components/InfoLote";
import StatusBadge from "../components/StatusBadge";
import type { CuentaOrdenante, LoteListItem } from "../types";
import { formatMoney, todayISO } from "../utils/format";

export default function Pagos() {
  const navigate = useNavigate();
  const [lotes, setLotes] = useState<LoteListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showNew, setShowNew] = useState(false);
  const [cuentas, setCuentas] = useState<CuentaOrdenante[]>([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    fecha_operacion: todayISO(),
    cuenta_ordenante_id: 0,
    concepto_general: "",
    fecha_limite: "",
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.lotes({ page, page_size: 20 });
      setLotes(res.items);
      setTotal(res.total);
      setPages(res.pages);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    load();
    api.cuentasOrdenantes().then((c) => {
      setCuentas(c);
      if (c.length) setForm((f) => ({ ...f, cuenta_ordenante_id: c[0].id }));
    });
  }, [load]);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const lote = await api.crearLote({
        fecha_operacion: form.fecha_operacion,
        cuenta_ordenante_id: form.cuenta_ordenante_id,
        concepto_general: form.concepto_general,
        fecha_limite: form.fecha_limite || null,
        pagos: [],
      });
      setShowNew(false);
      navigate(`/pagos/${lote.id}`);
      trackAction("pagos", `Lote creado #${lote.id}`, { lote_id: lote.id });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al crear lote");
    }
  };

  return (
    <>
      <div className="page-hero">
        <div>
          <h1 className="page-title">Pagos del viernes</h1>
          <p className="page-subtitle hero-sub">
            Cree y procese lotes de pago — archivo bancario y correos
          </p>
        </div>
        <button type="button" className="btn btn-primary btn-lg" onClick={() => setShowNew(true)}>
          + Nuevo lote
        </button>
      </div>

      <InfoLote />

      <div className="card">
        <div className="card-header">
          <h2>Historial de lotes</h2>
        </div>

        {loading ? (
          <p className="empty-state">Cargando…</p>
        ) : lotes.length ? (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Fecha</th>
                    <th>Concepto</th>
                    <th>Estado</th>
                    <th>Pagos</th>
                    <th>Total</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {lotes.map((l) => (
                    <tr key={l.id}>
                      <td>#{l.id}</td>
                      <td>{l.fecha_operacion}</td>
                      <td>{l.concepto_general}</td>
                      <td>
                        <StatusBadge estado={l.estado} />
                      </td>
                      <td>{l.cantidad_pagos}</td>
                      <td className="money">{formatMoney(l.importe_total)}</td>
                      <td>
                        <Link to={`/pagos/${l.id}`} className="btn btn-outline btn-sm">
                          Abrir
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pagination">
              <button
                type="button"
                className="btn btn-outline btn-sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Anterior
              </button>
              <span>
                Página {page} de {pages} ({total} total)
              </span>
              <button
                type="button"
                className="btn btn-outline btn-sm"
                disabled={page >= pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Siguiente
              </button>
            </div>
          </>
        ) : (
          <p className="empty-state">
            No hay lotes. Crea un nuevo lote para comenzar el proceso del viernes.
          </p>
        )}
      </div>

      {showNew && (
        <div className="modal-overlay" onClick={() => setShowNew(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Nuevo lote de pago</h3>
            {error && <div className="alert alert-error">{error}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Fecha operación</label>
                  <input
                    type="date"
                    value={form.fecha_operacion}
                    onChange={(e) => setForm({ ...form, fecha_operacion: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Fecha límite (opcional)</label>
                  <input
                    type="date"
                    value={form.fecha_limite}
                    onChange={(e) => setForm({ ...form, fecha_limite: e.target.value })}
                  />
                </div>
                <div className="form-group full">
                  <label>Cuenta ordenante</label>
                  <select
                    value={form.cuenta_ordenante_id}
                    onChange={(e) =>
                      setForm({ ...form, cuenta_ordenante_id: +e.target.value })
                    }
                    required
                  >
                    {cuentas.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.alias} — {c.numero_cuenta}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group full">
                  <label>Concepto general</label>
                  <input
                    value={form.concepto_general}
                    onChange={(e) => setForm({ ...form, concepto_general: e.target.value })}
                    placeholder="Ej: PAGO PROVEEDORES SEMANA 25"
                    required
                    maxLength={120}
                  />
                </div>
              </div>
              <div className="btn-group" style={{ marginTop: "1.25rem" }}>
                <button type="submit" className="btn btn-primary">
                  Crear y abrir
                </button>
                <button type="button" className="btn btn-outline" onClick={() => setShowNew(false)}>
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
