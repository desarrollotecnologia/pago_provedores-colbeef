export interface UsuarioAuth {
  id: number;
  username: string;
  nombre_completo: string;
  rol: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  usuario: UsuarioAuth;
}

export interface PublicConfig {
  app_name: string;
  app_url: string;
  api_base: string;
  version: string;
  env: string;
  email_template_version?: string;
  ui_version?: string;
}

export interface CatalogoItem {
  codigo: number;
  descripcion: string;
}

export interface BancoCatalogo {
  codigo: number;
  descripcion: string;
}

export interface Proveedor {
  id: number;
  identificacion: string;
  tipo_identificacion: number;
  digito_verificacion: number | null;
  razon_social: string;
  forma_pago: number;
  banco_codigo: number;
  tipo_cuenta: number;
  numero_cuenta: string;
  cod_oficina: string | null;
  email: string | null;
  activo: boolean;
  creado_en: string;
  actualizado_en: string;
  banco?: { codigo: number; descripcion: string };
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Pago {
  id: number;
  proveedor_id: number;
  identificacion: string;
  tipo_identificacion: number;
  digito_verificacion: number | null;
  razon_social: string;
  banco_codigo: number;
  tipo_cuenta: number;
  numero_cuenta: string;
  cod_oficina: string | null;
  forma_pago: number;
  importe: string;
  fecha_limite: string | null;
  concepto1: string | null;
  concepto2: string | null;
  concepto3: string | null;
  concepto4: string | null;
  numero_factura: string | null;
  email_destino: string | null;
  referencia_16: string | null;
  referencia_11: string | null;
  estado: string;
}

export interface Lote {
  id: number;
  fecha_operacion: string;
  fecha_limite: string | null;
  cuenta_ordenante_id: number;
  concepto_general: string;
  estado: string;
  importe_total: string;
  cantidad_pagos: number;
  archivo_plano_nombre: string | null;
  usuario_id: number;
  creado_en: string;
  pagos: Pago[];
}

export interface LoteListItem {
  id: number;
  fecha_operacion: string;
  concepto_general: string;
  estado: string;
  importe_total: string;
  cantidad_pagos: number;
  archivo_plano_nombre: string | null;
  creado_en: string;
}

export interface CuentaOrdenante {
  id: number;
  alias: string;
  numero_cuenta: string;
}

export interface HistorialPagoItem {
  id: number;
  lote_id: number;
  lote_fecha_operacion: string;
  lote_concepto: string;
  lote_estado: string;
  proveedor_id: number;
  razon_social: string;
  identificacion: string;
  importe: string;
  numero_factura: string | null;
  concepto1: string | null;
  estado: string;
  email_destino: string | null;
}

export interface HistorialPagosResponse {
  resumen: {
    fecha_desde: string;
    fecha_hasta: string;
    importe_total: string;
    cantidad_pagos: number;
  };
  items: HistorialPagoItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface CambioCampo {
  campo: string;
  etiqueta: string;
  anterior: string | null;
  nuevo: string | null;
}

export interface CambioProveedorItem {
  id: number;
  registrado_en: string;
  accion: string;
  proveedor_id: number;
  razon_social: string;
  identificacion: string;
  usuario_id: number;
  usuario_nombre: string;
  resumen: string;
  cantidad_cambios: number;
}

export interface CambioProveedorDetalle extends CambioProveedorItem {
  cambios: CambioCampo[];
  snapshot: Record<string, unknown> | null;
}

export interface CambiosProveedorResponse {
  resumen: {
    fecha_desde: string;
    fecha_hasta: string;
    cantidad_cambios: number;
    creaciones: number;
    ediciones: number;
    desactivaciones: number;
  };
  items: CambioProveedorItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface HistorialPagoDetalle {
  id: number;
  lote_id: number;
  lote_fecha_operacion: string;
  lote_fecha_limite: string | null;
  lote_concepto: string;
  lote_estado: string;
  lote_importe_total: string;
  lote_archivo: string | null;
  proveedor_id: number;
  identificacion: string;
  tipo_identificacion: number;
  digito_verificacion: number | null;
  razon_social: string;
  banco_codigo: number;
  banco_descripcion: string | null;
  tipo_cuenta: number;
  numero_cuenta: string;
  cod_oficina: string | null;
  forma_pago: number;
  importe: string;
  fecha_limite: string | null;
  concepto1: string | null;
  concepto2: string | null;
  concepto3: string | null;
  concepto4: string | null;
  numero_factura: string | null;
  email_destino: string | null;
  referencia_16: string | null;
  referencia_11: string | null;
  estado: string;
}

export interface DashboardResponse {
  resumen: {
    fecha_desde: string;
    fecha_hasta: string;
    importe_total: string;
    cantidad_proveedores: number;
    cantidad_lotes: number;
    cantidad_pagos: number;
  };
  top_proveedores: {
    proveedor_id: number;
    razon_social: string;
    total_pagado: string;
    cantidad_pagos: number;
  }[];
  ultimos_lotes: {
    id: number;
    fecha_operacion: string;
    concepto?: string;
    concepto_general: string;
    estado: string;
    importe_total: string;
    cantidad_pagos: number;
  }[];
}

export interface ProcesarLoteResponse {
  lote_id: number;
  archivo: string;
  ruta: string;
  lineas: number;
  correos_enviados?: number;
  correos_error?: number;
  mensaje: string;
}

export interface UsabilityStats {
  periodo_dias: number;
  desde: string;
  kpis: {
    total_eventos: number;
    usuarios_unicos: number;
    sesiones_unicas: number;
    ultima_actividad: {
      usuario: string | null;
      action: string | null;
      module: string | null;
      detail: string | null;
      timestamp: string | null;
    };
  };
  eventos_por_dia: { dia: string; total: number }[];
  top_usuarios: { usuario: string; total: number }[];
  por_modulo: { module: string; total: number }[];
  por_accion: { action: string; total: number }[];
  recientes: {
    timestamp: string;
    usuario: string;
    action: string;
    module: string;
    detail: string | null;
    page: string | null;
  }[];
}

export interface SmtpStatus {
  configured: boolean;
  host: string | null;
  from_email: string;
}
