import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, api } from "../api/client";
import { getToken } from "../auth/session";
import { trackAction } from "../telemetry/tracker";
import InfoLote from "../components/InfoLote";
import ProveedorSearch from "../components/ProveedorSearch";
import StatusBadge from "../components/StatusBadge";
import type { Lote, Proveedor } from "../types";
import { formatMoney } from "../utils/format";

export default function LoteDetail() {
  const { id } = useParams<{ id: string }>();
  const loteId = Number(id);
  const [lote, setLote] = useState<Lote | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [processing, setProcessing] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [selectedProv, setSelectedProv] = useState<Proveedor | null>(null);
  const [pagoForm, setPagoForm] = useState({
    importe: "",
    numero_factura: "",
    concepto1: "",
    email_destino: "",
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.lote(loteId);
      setLote(data);
    } finally {
      setLoading(false);
    }
  }, [loteId]);

  useEffect(() => {
    load();
  }, [load]);

  const openAddModal = () => {
    setError("");
    setSelectedProv(null);
    setShowAdd(true);
  };

  const closeAddModal = () => {
    setShowAdd(false);
    setSelectedProv(null);
    setError("");
  };

  const handleSelectProveedor = (p: Proveedor) => {
    setSelectedProv(p);
    setPagoForm((f) => ({
      ...f,
      email_destino: p.email ?? "",
    }));
  };

  const handleAddPago = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedProv) return;
    setError("");
    try {
      await api.agregarPago(loteId, {
        proveedor_id: selectedProv.id,
        importe: parseFloat(pagoForm.importe),
        numero_factura: pagoForm.numero_factura || null,
        concepto1: pagoForm.concepto1 || null,
        email_destino: pagoForm.email_destino || selectedProv.email,
      });
      setShowAdd(false);
      setSelectedProv(null);
      setPagoForm({ importe: "", numero_factura: "", concepto1: "", email_destino: "" });
      load();
      setMessage("Pago agregado al lote");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al agregar pago");
    }
  };

  const handleDeletePago = async (pagoId: number) => {
    if (!confirm("¿Eliminar este pago del lote?")) return;
    await api.eliminarPago(pagoId);
    load();
    setMessage("Pago eliminado");
  };

  const runAction = async (action: "archivo" | "correos" | "procesar" | "procesar-sin-correos") => {
    setProcessing(true);
    setError("");
    setMessage("");
    try {
      let res;
      if (action === "archivo") res = await api.generarArchivo(loteId);
      else if (action === "correos") res = await api.enviarCorreos(loteId);
      else if (action === "procesar") res = await api.procesarLote(loteId, true);
      else res = await api.procesarLote(loteId, false);
      setMessage(res.mensaje);
      load();
      if (action === "archivo") trackAction("pagos", `Archivo generado lote #${loteId}`);
      else if (action === "correos") trackAction("pagos", `Correos enviados lote #${loteId}`);
      else if (action === "procesar") trackAction("pagos", `Procesar todo lote #${loteId}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error en la operación");
    } finally {
      setProcessing(false);
    }
  };

  const downloadArchivo = () => {
    const token = getToken();
    const url = api.descargarArchivoUrl(loteId);
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = lote?.archivo_plano_nombre ?? "pagos.txt";
        a.click();
      });
  };

  if (loading) return <p className="page-subtitle">Cargando lote…</p>;
  if (!lote) return <p className="alert alert-error">Lote no encontrado</p>;

  const editable = lote.estado === "borrador";

  return (
    <>
      <div style={{ marginBottom: "0.5rem" }}>
        <Link to="/pagos" style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
          ← Volver a lotes
        </Link>
      </div>

      <div className="card-header" style={{ marginBottom: "1rem" }}>
        <div>
          <h1 className="page-title">Lote #{lote.id}</h1>
          <p className="page-subtitle" style={{ marginBottom: 0 }}>
            {lote.concepto_general} — <StatusBadge estado={lote.estado} />
          </p>
        </div>
        <div className="btn-group">
          {editable && (
            <button type="button" className="btn btn-primary" onClick={openAddModal}>
              + Agregar pago
            </button>
          )}
          <button
            type="button"
            className="btn btn-secondary"
            disabled={processing || !lote.pagos.length}
            onClick={() => runAction("archivo")}
          >
            Generar archivo
          </button>
          {lote.archivo_plano_nombre && (
            <button type="button" className="btn btn-outline" onClick={downloadArchivo}>
              Descargar TXT
            </button>
          )}
          <button
            type="button"
            className="btn btn-secondary"
            disabled={processing || !lote.archivo_plano_nombre}
            onClick={() => runAction("correos")}
          >
            Enviar correos
          </button>
          <button
            type="button"
            className="btn btn-primary"
            disabled={processing || !lote.pagos.length}
            onClick={() => runAction("procesar")}
          >
            Procesar todo
          </button>
        </div>
      </div>

      {message && (
        <div
          className={`alert ${
            /errores:\s*[1-9]/i.test(message) ? "alert-success-warn" : "alert-success"
          }`}
        >
          {message}
        </div>
      )}
      {error && <div className="alert alert-error">{error}</div>}

      {editable && <InfoLote compact />}

      <div className="cards-grid">
        <div className="stat-card">
          <div className="label">Fecha operación</div>
          <div className="value" style={{ fontSize: "1.1rem" }}>
            {lote.fecha_operacion}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">Pagos</div>
          <div className="value">{lote.cantidad_pagos}</div>
        </div>
        <div className="stat-card">
          <div className="label">Importe total</div>
          <div className="value">{formatMoney(lote.importe_total)}</div>
        </div>
        <div className="stat-card">
          <div className="label">Archivo plano</div>
          <div className="value" style={{ fontSize: "0.85rem" }}>
            {lote.archivo_plano_nombre ?? "—"}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Pagos del lote</h2>
        </div>
        {lote.pagos.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Proveedor</th>
                  <th>NIT</th>
                  <th>Cuenta</th>
                  <th>Importe</th>
                  <th>Factura</th>
                  <th>Estado</th>
                  {editable && <th></th>}
                </tr>
              </thead>
              <tbody>
                {lote.pagos.map((p) => (
                  <tr key={p.id}>
                    <td>{p.razon_social}</td>
                    <td>{p.identificacion}</td>
                    <td>{p.numero_cuenta}</td>
                    <td className="money">{formatMoney(p.importe)}</td>
                    <td>{p.numero_factura ?? "—"}</td>
                    <td>
                      <StatusBadge estado={p.estado} />
                    </td>
                    {editable && (
                      <td>
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDeletePago(p.id)}
                        >
                          Quitar
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="empty-state">Agrega proveedores e importes a este lote.</p>
        )}
      </div>

      {showAdd && (
        <div className="modal-overlay" onClick={closeAddModal}>
          <div className="modal modal-wide" onClick={(e) => e.stopPropagation()}>
            <h3>Agregar pago al lote</h3>
            {error && <div className="alert alert-error">{error}</div>}

            {!selectedProv ? (
              <ProveedorSearch onSelect={handleSelectProveedor} />
            ) : (
              <form onSubmit={handleAddPago}>
                <div className="alert alert-info">
                  <strong>{selectedProv.razon_social}</strong> — {selectedProv.identificacion}
                  <button
                    type="button"
                    className="btn btn-outline btn-sm"
                    style={{ marginLeft: "0.5rem" }}
                    onClick={() => setSelectedProv(null)}
                  >
                    Cambiar
                  </button>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Importe</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={pagoForm.importe}
                      onChange={(e) => setPagoForm({ ...pagoForm, importe: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>N° factura</label>
                    <input
                      value={pagoForm.numero_factura}
                      onChange={(e) => setPagoForm({ ...pagoForm, numero_factura: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Concepto</label>
                    <input
                      value={pagoForm.concepto1}
                      onChange={(e) => setPagoForm({ ...pagoForm, concepto1: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Email destino</label>
                    <input
                      type="email"
                      value={pagoForm.email_destino}
                      onChange={(e) => setPagoForm({ ...pagoForm, email_destino: e.target.value })}
                    />
                  </div>
                </div>
                <div className="btn-group" style={{ marginTop: "1rem" }}>
                  <button type="submit" className="btn btn-primary">
                    Agregar
                  </button>
                  <button type="button" className="btn btn-outline" onClick={closeAddModal}>
                    Cancelar
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
