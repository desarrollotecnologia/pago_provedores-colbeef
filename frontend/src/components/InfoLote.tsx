export default function InfoLote({ compact = false }: { compact?: boolean }) {
  if (compact) {
    return (
      <div className="info-banner">
        <strong>¿Qué es un lote?</strong> Es el grupo de pagos del viernes que usted arma en el
        sistema. <em>No viene del Excel</em> — el Excel solo carga proveedores una vez; el lote se
        crea aquí cada semana.
      </div>
    );
  }

  return (
    <div className="info-panel">
      <div className="info-panel-icon">i</div>
      <div>
        <h3>¿Para qué sirve un lote de pago?</h3>
        <p>
          Un <strong>lote</strong> agrupa los pagos que Colbeef enviará al banco en una fecha
          (normalmente el viernes). Desde el lote usted:
        </p>
        <ul>
          <li>Selecciona proveedores e importes a pagar esa semana</li>
          <li>Genera el <strong>archivo plano TXT</strong> para cargar en el banco</li>
          <li>Envía los <strong>correos de notificación</strong> a cada proveedor</li>
        </ul>
        <p className="info-note">
          <strong>Importante:</strong> el archivo Excel <em>no crea lotes</em>. El Excel solo importa
          el catálogo de proveedores (nombre, banco, cuenta). Cada lote se crea manualmente en
          <strong> Pagos → Nuevo lote</strong> cuando llega el día de pago.
        </p>
      </div>
    </div>
  );
}
