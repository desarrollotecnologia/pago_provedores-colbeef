import { useEffect, useRef } from "react";

export interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  detail?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "default" | "primary" | "danger";
  icon?: "mail" | "warning" | "trash" | "info";
  loading?: boolean;
  hideCancel?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

const ICONS = {
  mail: "✉",
  warning: "⚠",
  trash: "🗑",
  info: "ℹ",
} as const;

export default function ConfirmDialog({
  open,
  title,
  message,
  detail,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  variant = "primary",
  icon = "warning",
  loading = false,
  hideCancel = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const confirmRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const t = window.setTimeout(() => confirmRef.current?.focus(), 80);
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !loading) onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = prev;
      window.clearTimeout(t);
      window.removeEventListener("keydown", onKey);
    };
  }, [open, loading, onCancel]);

  if (!open) return null;

  return (
    <div
      className="confirm-overlay"
      role="presentation"
      onClick={loading ? undefined : onCancel}
    >
      <div
        className="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        aria-describedby="confirm-desc"
        onClick={(e) => e.stopPropagation()}
      >
        <div className={`confirm-dialog-icon confirm-dialog-icon--${variant}`}>
          {ICONS[icon]}
        </div>
        <h2 id="confirm-title" className="confirm-dialog-title">
          {title}
        </h2>
        <p id="confirm-desc" className="confirm-dialog-message">
          {message}
        </p>
        {detail && <p className="confirm-dialog-detail">{detail}</p>}
        <div className="confirm-dialog-actions">
          {!hideCancel && (
            <button
              type="button"
              className="btn btn-outline"
              disabled={loading}
              onClick={onCancel}
            >
              {cancelLabel}
            </button>
          )}
          <button
            ref={confirmRef}
            type="button"
            className={`btn ${
              variant === "danger" ? "btn-danger" : "btn-primary"
            }`}
            disabled={loading}
            onClick={onConfirm}
          >
            {loading ? "Procesando…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
