import { useEffect } from "react";
import InfoLote from "../components/InfoLote";
import { useAuth } from "../context/AuthContext";
import { track } from "../telemetry/tracker";

const FLUJO_ADMIN = [
  {
    n: 1,
    title: "Iniciar sesión como administrador",
    desc: "Solo el usuario con rol admin puede crear lotes y procesar pagos.",
  },
  {
    n: 2,
    title: "Ir a Pagos → Nuevo lote",
    desc: "Cada viernes se crea un lote nuevo con fecha y concepto del pago semanal.",
  },
  {
    n: 3,
    title: "Agregar proveedores e importes",
    desc: "Busque en el catálogo (cargado desde Excel) y asigne el valor a pagar.",
  },
  {
    n: 4,
    title: "Generar archivo plano",
    desc: "Descargue el archivo TXT de 281 caracteres para cargarlo en el banco.",
  },
  {
    n: 5,
    title: "Enviar correos",
    desc: "Notifique a cada proveedor sobre su pago. Puede usar «Procesar todo».",
  },
];

const GLOSARIO = [
  {
    term: "Proveedor",
    def: "Empresa o persona a la que Colbeef paga. Sus datos vienen del Excel importado una vez.",
  },
  {
    term: "Lote de pago",
    def: "Grupo de pagos de una semana. Se crea manualmente cada viernes — no viene del Excel.",
  },
  {
    term: "Archivo plano",
    def: "Archivo TXT que el banco recibe con todos los pagos del lote.",
  },
  {
    term: "Excel operativo",
    def: "Solo importa el catálogo de proveedores (NIT, banco, cuenta). No genera lotes.",
  },
];

export default function OperadorDashboard() {
  const { user, config } = useAuth();

  useEffect(() => {
    track("module_open", "guia_uso", "Panel de usabilidad — operador");
  }, []);

  return (
    <>
      <div className="page-hero operador-hero">
        <div>
          <p className="hero-eyebrow">Guía de uso del sistema</p>
          <h1 className="page-title">Bienvenido, {user?.nombre_completo ?? user?.username}</h1>
          <p className="page-subtitle hero-sub">
            Esta vista es informativa. Las operaciones las realiza el administrador de tesorería.
          </p>
        </div>
        <div className="readonly-badge">Solo consulta</div>
      </div>

      <div className="alert alert-info">
        <strong>Su perfil (operador)</strong> permite consultar cómo funciona el programa. Para crear
        lotes, pagos o modificar proveedores, contacte al administrador (
        <em>viviana</em>).
      </div>

      <InfoLote />

      <div className="card">
        <div className="card-header">
          <h2>Flujo del viernes (realiza el administrador)</h2>
        </div>
        <div className="workflow-steps workflow-steps-static">
          {FLUJO_ADMIN.map((s) => (
            <div key={s.n} className="workflow-step workflow-step-static">
              <span className="workflow-num">{s.n}</span>
              <div>
                <strong>{s.title}</strong>
                <p>{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="two-cols">
        <div className="card">
          <div className="card-header">
            <h2>Glosario</h2>
          </div>
          <dl className="glossary">
            {GLOSARIO.map((g) => (
              <div key={g.term} className="glossary-item">
                <dt>{g.term}</dt>
                <dd>{g.def}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="card card-muted">
          <div className="card-header">
            <h2>Información del sistema</h2>
          </div>
          <ul className="info-list">
            <li>
              <span>URL</span>
              <strong>{config?.app_url ?? "—"}</strong>
            </li>
            <li>
              <span>Versión</span>
              <strong>{config?.version ?? "1.0"}</strong>
            </li>
            <li>
              <span>Su rol</span>
              <strong>Operador (guía de uso)</strong>
            </li>
            <li>
              <span>Operaciones</span>
              <strong>Administrador</strong>
            </li>
          </ul>
          <p className="card-text-muted" style={{ marginTop: "1rem" }}>
            Si necesita ejecutar pagos, solicite acceso de administrador al área de sistemas o
            tesorería.
          </p>
        </div>
      </div>
    </>
  );
}
