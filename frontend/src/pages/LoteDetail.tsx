import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, api } from "../api/client";
import { getToken } from "../auth/session";
import ConfirmDialog from "../components/ConfirmDialog";
import { trackAction } from "../telemetry/tracker";
import InfoLote from "../components/InfoLote";
import ProveedorSearch from "../components/ProveedorSearch";
import StatusBadge from "../components/StatusBadge";
import type { Lote, Pago, Proveedor } from "../types";
import { formatMoney } from "../utils/format";
import {
  camposFaltantesPago,
  mensajeCamposFaltantes,
  pagoIncompleto,
  type PagoFormData,
} from "../utils/pagoValidation";

const EMPTY_PAGO_FORM: PagoFormData = {
  importe: "",
  numero_factura: "",
  concepto1: "",
  email_destino: "",
};

type LoteAction = "archivo" | "correos" | "procesar" | "procesar-sin-correos" | "finalizar";

interface ConfirmState {
  title: string;
  message: string;
  detail?: string;
  confirmLabel: string;
  variant: "primary" | "danger";
  icon: "mail" | "warning" | "trash";
  action: LoteAction | "delete-pago";
  pagoId?: number;
}

export default function LoteDetail() {
  const { id } = useParams<{ id: string }>();
  const loteId = Number(id);
  const [lote, setLote] = useState<Lote | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [processing, setProcessing] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [editingPago, setEditingPago] = useState<Pago | null>(null);
  const [selectedProv, setSelectedProv] = useState<Proveedor | null>(null);
  const [pagoForm, setPagoForm] = useState<PagoFormData>(EMPTY_PAGO_FORM);
  const [confirmState, setConfirmState] = useState<ConfirmState | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [infoDialog, setInfoDialog] = useState<{ title: string; message: string } | null>(
    null
  );

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
    setEditingPago(null);
    setSelectedProv(null);
    setPagoForm(EMPTY_PAGO_FORM);
    setShowAdd(true);
  };

  const closeAddModal = () => {
    setShowAdd(false);
    setSelectedProv(null);
    setPagoForm(EMPTY_PAGO_FORM);
    setError("");
  };

  const openEditModal = (pago: Pago) => {
    setError("");
    setShowAdd(false);
    setEditingPago(pago);
    setPagoForm({
      importe: pago.importe,
      numero_factura: pago.numero_factura ?? "",
      concepto1: pago.concepto1 ?? "",
      email_destino: pago.email_destino ?? "",
    });
  };

  const closeEditModal = () => {
    setEditingPago(null);
    setPagoForm(EMPTY_PAGO_FORM);
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
    const faltantes = camposFaltantesPago(pagoForm);
    if (faltantes.length) {
      setError(mensajeCamposFaltantes(faltantes));
      return;
    }
    setError("");
    try {
      await api.agregarPago(loteId, {
        proveedor_id: selectedProv.id,
        importe: parseFloat(pagoForm.importe),
        numero_factura: pagoForm.numero_factura.trim(),
        concepto1: pagoForm.concepto1.trim(),
        email_destino: pagoForm.email_destino.trim(),
      });
      closeAddModal();
      load();
      setMessage("Pago agregado al lote");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al agregar pago");
    }
  };

  const handleEditPago = async (e: FormEvent) => {
    e.preventDefault();
    if (!editingPago) return;
    const faltantes = camposFaltantesPago(pagoForm);
    if (faltantes.length) {
      setError(mensajeCamposFaltantes(faltantes));
      return;
    }
    setError("");
    try {
      await api.actualizarPago(editingPago.id, {
        importe: parseFloat(pagoForm.importe),
        numero_factura: pagoForm.numero_factura.trim(),
        concepto1: pagoForm.concepto1.trim(),
        email_destino: pagoForm.email_destino.trim(),
      });
      closeEditModal();
      load();
      setMessage("Pago actualizado");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al actualizar pago");
    }
  };

  const handleDeletePago = (pagoId: number) => {
    setConfirmState({
      title: "Eliminar pago",
      message: "¿Desea quitar este pago del lote?",
      detail: "Esta acción no se puede deshacer.",
      confirmLabel: "Eliminar",
      variant: "danger",
      icon: "trash",
      action: "delete-pago",
      pagoId,
    });
  };

  const downloadArchivo = async (nombre?: string) => {
    const token = getToken();
    const url = api.descargarArchivoUrl(loteId);
    const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) throw new Error("No se pudo descargar el archivo plano");
    const blob = await res.blob();
    const a = document.createElement("a");
    const objectUrl = URL.createObjectURL(blob);
    a.href = objectUrl;
    a.download = nombre ?? lote?.archivo_plano_nombre ?? "pagos.txt";
    a.click();
    URL.revokeObjectURL(objectUrl);
  };

  const executeAction = async (action: LoteAction) => {
    if (!lote) return;
    setProcessing(true);
    setError("");
    setMessage("");
    try {
      let res;
      if (action === "archivo") res = await api.generarArchivo(loteId);
      else if (action === "correos") res = await api.enviarCorreos(loteId);
      else if (action === "finalizar" || action === "procesar")
        res = await api.procesarLote(loteId, true);
      else res = await api.procesarLote(loteId, false);

      if (action === "finalizar") {
        await downloadArchivo(res.archivo);
        setMessage(`${res.mensaje} — Archivo descargado.`);
      } else {
        setMessage(res.mensaje);
      }

      await load();

      if (action === "archivo") trackAction("pagos", `Archivo generado lote #${loteId}`);
      else if (action === "correos") trackAction("pagos", `Correos enviados lote #${loteId}`);
      else if (action === "finalizar" || action === "procesar")
        trackAction("pagos", `Lote finalizado #${loteId}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error en la operación");
    } finally {
      setProcessing(false);
    }
  };

  const handleConfirm = async () => {
    if (!confirmState) return;
    const { action, pagoId } = confirmState;
    setConfirmState(null);

    if (action === "delete-pago" && pagoId != null) {
      try {
        await api.eliminarPago(pagoId);
        load();
        setMessage("Pago eliminado");
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Error al eliminar pago");
      }
      return;
    }

    await executeAction(action as LoteAction);
  };

  const pagosActivos = lote?.pagos.filter((p) => p.estado !== "anulado") ?? [];
  const totalPagosActivos = pagosActivos.reduce((sum, p) => sum + Number(p.importe || 0), 0);
  const pagosIncompletos = pagosActivos.filter(pagoIncompleto);

  const validarAntesDeProcesar = (): boolean => {
    if (!lote || pagosIncompletos.length === 0) return true;
    const nombres = pagosIncompletos
      .slice(0, 4)
      .map((p) => p.razon_social)
      .join(", ");
    const extra =
      pagosIncompletos.length > 4 ? ` y ${pagosIncompletos.length - 4} más` : "";
    setInfoDialog({
      title: "Pagos incompletos",
      message: `${pagosIncompletos.length} pago(s) tienen datos faltantes (factura, concepto o email). Edítelos antes de procesar. Proveedores: ${nombres}${extra}.`,
    });
    return false;
  };

  const runAction = (action: LoteAction) => {
    if (!lote) return;

    if (
      (action === "archivo" ||
        action === "correos" ||
        action === "procesar" ||
        action === "finalizar") &&
      !validarAntesDeProcesar()
    ) {
      return;
    }

    const yaEnviados =
      lote.estado === "correos_enviados" || lote.estado === "completado";
    const pendientes = lote.pagos.filter(
      (p) => p.estado !== "anulado" && p.estado !== "correo_enviado"
    ).length;

    if (action === "correos" || action === "procesar" || action === "finalizar") {
      if (yaEnviados) {
        setInfoDialog({
          title: "Lote ya finalizado",
          message: "Este lote ya fue procesado y los correos fueron enviados.",
        });
        return;
      }
      if (pendientes === 0) {
        setInfoDialog({
          title: "Sin correos pendientes",
          message: "No hay correos pendientes por enviar en este lote.",
        });
        return;
      }

      if (action === "finalizar") {
        setConfirmState({
          title: "¿Finalizar lote?",
          message: `Se generará el archivo plano bancario, se descargará el TXT a su equipo y se enviarán ${pendientes} correo(s) a los proveedores.`,
          detail: "Solo se permite un envío por lote. Esta acción no se puede deshacer.",
          confirmLabel: "Sí, finalizar",
          variant: "primary",
          icon: "mail",
          action,
        });
        return;
      }

      const esProcesar = action === "procesar";
      setConfirmState({
        title: esProcesar ? "Procesar lote completo" : "Enviar correos",
        message: esProcesar
          ? `Se generará el archivo plano y se enviarán ${pendientes} correo(s) a los proveedores.`
          : `Se enviarán ${pendientes} correo(s) de soporte de pago a los proveedores.`,
        detail: "Solo se permite un envío por lote. Esta acción no se puede deshacer.",
        confirmLabel: esProcesar ? "Procesar todo" : "Enviar correos",
        variant: "primary",
        icon: "mail",
        action,
      });
      return;
    }

    void executeAction(action);
  };

  if (loading) return <p className="page-subtitle">Cargando lote…</p>;
  if (!lote) return <p className="alert alert-error">Lote no encontrado</p>;

  const editable = lote.estado === "borrador" || lote.estado === "confirmado";
  const correosYaEnviados =
    lote.estado === "correos_enviados" || lote.estado === "completado";
  const hayPagosIncompletos = pagosIncompletos.length > 0;
  const puedeFinalizar =
    !correosYaEnviados && pagosActivos.length > 0 && !hayPagosIncompletos && !processing;
  const puedeEnviarCorreos =
    Boolean(lote.archivo_plano_nombre) && !correosYaEnviados && !processing && !hayPagosIncompletos;

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
        <div className="lote-actions">
          {editable && (
            <button type="button" className="btn btn-outline" onClick={openAddModal}>
              + Agregar pago
            </button>
          )}

          {!correosYaEnviados ? (
            <button
              type="button"
              className="btn btn-primary btn-lg lote-btn-finalizar"
              disabled={!puedeFinalizar}
              title={
                hayPagosIncompletos
                  ? "Complete todos los pagos antes de finalizar"
                  : pagosActivos.length === 0
                    ? "Agregue al menos un pago"
                    : "Genera archivo, descarga TXT y envía correos"
              }
              onClick={() => runAction("finalizar")}
            >
              {processing ? "Finalizando…" : "Finalizar lote"}
            </button>
          ) : (
            pagosActivos.length > 0 && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => void downloadArchivo()}
              >
                Descargar TXT
              </button>
            )
          )}

          {!correosYaEnviados && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => setShowAdvanced((v) => !v)}
            >
              {showAdvanced ? "Ocultar opciones ▴" : "Más opciones ▾"}
            </button>
          )}
        </div>
      </div>

      {showAdvanced && !correosYaEnviados && (
        <div className="lote-advanced-actions card">
          <p className="lote-advanced-label">Pasos individuales (solo si lo necesita)</p>
          <div className="btn-group">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={processing || !pagosActivos.length || hayPagosIncompletos}
              onClick={() => runAction("archivo")}
            >
              Solo generar archivo
            </button>
            {pagosActivos.length > 0 && (
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => void downloadArchivo()}
              >
                Descargar TXT
              </button>
            )}
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={!puedeEnviarCorreos}
              onClick={() => runAction("correos")}
            >
              Solo enviar correos
            </button>
          </div>
        </div>
      )}

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

      {hayPagosIncompletos && editable && (
        <div className="alert alert-warn">
          {pagosIncompletos.length} pago(s) con datos incompletos. Use <strong>Editar</strong> para
          completar factura, concepto y email antes de generar el archivo o enviar correos.
        </div>
      )}

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
          <div className="value">{formatMoney(totalPagosActivos)}</div>
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
                  <th>Concepto</th>
                  <th>Email</th>
                  <th>Estado</th>
                  {editable && <th></th>}
                </tr>
              </thead>
              <tbody>
                {lote.pagos.map((p) => (
                  <tr key={p.id} className={pagoIncompleto(p) && p.estado !== "anulado" ? "row-warning" : ""}>
                    <td>{p.razon_social}</td>
                    <td>{p.identificacion}</td>
                    <td>{p.numero_cuenta}</td>
                    <td className="money">{formatMoney(p.importe)}</td>
                    <td>{p.numero_factura?.trim() || "—"}</td>
                    <td>{p.concepto1?.trim() || "—"}</td>
                    <td>{p.email_destino?.trim() || "—"}</td>
                    <td>
                      <StatusBadge estado={p.estado} />
                      {pagoIncompleto(p) && p.estado !== "anulado" && (
                        <span className="badge-incomplete" title="Datos incompletos">
                          Incompleto
                        </span>
                      )}
                    </td>
                    {editable && p.estado !== "anulado" && (
                      <td>
                        <div className="btn-group">
                          <button
                            type="button"
                            className="btn btn-outline btn-sm"
                            onClick={() => openEditModal(p)}
                          >
                            Editar
                          </button>
                          <button
                            type="button"
                            className="btn btn-danger btn-sm"
                            onClick={() => handleDeletePago(p.id)}
                          >
                            Quitar
                          </button>
                        </div>
                      </td>
                    )}
                    {editable && p.estado === "anulado" && <td></td>}
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
                    <label>Importe *</label>
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
                    <label>N° factura *</label>
                    <input
                      value={pagoForm.numero_factura}
                      onChange={(e) => setPagoForm({ ...pagoForm, numero_factura: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Concepto *</label>
                    <input
                      value={pagoForm.concepto1}
                      onChange={(e) => setPagoForm({ ...pagoForm, concepto1: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Email destino *</label>
                    <input
                      type="email"
                      value={pagoForm.email_destino}
                      onChange={(e) => setPagoForm({ ...pagoForm, email_destino: e.target.value })}
                      required
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

      {editingPago && (
        <div className="modal-overlay" onClick={closeEditModal}>
          <div className="modal modal-wide" onClick={(e) => e.stopPropagation()}>
            <h3>Editar pago</h3>
            {error && <div className="alert alert-error">{error}</div>}
            <div className="alert alert-info">
              <strong>{editingPago.razon_social}</strong> — {editingPago.identificacion}
            </div>
            <form onSubmit={handleEditPago}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Importe *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={pagoForm.importe}
                    onChange={(e) => setPagoForm({ ...pagoForm, importe: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>N° factura *</label>
                  <input
                    value={pagoForm.numero_factura}
                    onChange={(e) => setPagoForm({ ...pagoForm, numero_factura: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Concepto *</label>
                  <input
                    value={pagoForm.concepto1}
                    onChange={(e) => setPagoForm({ ...pagoForm, concepto1: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Email destino *</label>
                  <input
                    type="email"
                    value={pagoForm.email_destino}
                    onChange={(e) => setPagoForm({ ...pagoForm, email_destino: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="btn-group" style={{ marginTop: "1rem" }}>
                <button type="submit" className="btn btn-primary">
                  Guardar cambios
                </button>
                <button type="button" className="btn btn-outline" onClick={closeEditModal}>
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={confirmState !== null}
        title={confirmState?.title ?? ""}
        message={confirmState?.message ?? ""}
        detail={confirmState?.detail}
        confirmLabel={confirmState?.confirmLabel}
        variant={confirmState?.variant}
        icon={confirmState?.icon}
        loading={processing}
        onConfirm={() => void handleConfirm()}
        onCancel={() => !processing && setConfirmState(null)}
      />

      <ConfirmDialog
        open={infoDialog !== null}
        title={infoDialog?.title ?? ""}
        message={infoDialog?.message ?? ""}
        confirmLabel="Entendido"
        variant="default"
        icon="info"
        hideCancel
        onConfirm={() => setInfoDialog(null)}
        onCancel={() => setInfoDialog(null)}
      />
    </>
  );
}
