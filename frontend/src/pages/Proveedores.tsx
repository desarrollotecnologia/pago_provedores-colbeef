import { FormEvent, useCallback, useEffect, useState } from "react";
import { ApiError, api } from "../api/client";
import type { BancoCatalogo, CatalogoItem, Proveedor } from "../types";

interface ProveedorFormProps {
  initial?: Proveedor | null;
  bancos: BancoCatalogo[];
  tiposId: CatalogoItem[];
  tiposCuenta: CatalogoItem[];
  onSave: () => void;
  onClose: () => void;
}

function ProveedorForm({ initial, bancos, tiposId, tiposCuenta, onSave, onClose }: ProveedorFormProps) {
  const [form, setForm] = useState({
    identificacion: initial?.identificacion ?? "",
    tipo_identificacion: initial?.tipo_identificacion ?? 3,
    digito_verificacion: initial?.digito_verificacion?.toString() ?? "",
    razon_social: initial?.razon_social ?? "",
    forma_pago: initial?.forma_pago ?? 1,
    banco_codigo: initial?.banco_codigo ?? bancos[0]?.codigo ?? 1,
    tipo_cuenta: initial?.tipo_cuenta ?? 1,
    numero_cuenta: initial?.numero_cuenta ?? "",
    email: initial?.email ?? "",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    const payload = {
      ...form,
      digito_verificacion: form.digito_verificacion ? parseInt(form.digito_verificacion, 10) : null,
      email: form.email || null,
    };
    try {
      if (initial) {
        await api.actualizarProveedor(initial.id, payload);
      } else {
        await api.crearProveedor(payload);
      }
      onSave();
      onClose();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>{initial ? "Editar proveedor" : "Nuevo proveedor"}</h3>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Tipo identificación</label>
              <select
                value={form.tipo_identificacion}
                onChange={(e) => setForm({ ...form, tipo_identificacion: +e.target.value })}
              >
                {tiposId.map((t) => (
                  <option key={t.codigo} value={t.codigo}>
                    {t.descripcion}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Identificación</label>
              <input
                value={form.identificacion}
                onChange={(e) => setForm({ ...form, identificacion: e.target.value })}
                required
              />
            </div>
            {form.tipo_identificacion === 3 && (
              <div className="form-group">
                <label>Dígito verificación</label>
                <input
                  value={form.digito_verificacion}
                  onChange={(e) => setForm({ ...form, digito_verificacion: e.target.value })}
                  maxLength={1}
                />
              </div>
            )}
            <div className="form-group full">
              <label>Razón social</label>
              <input
                value={form.razon_social}
                onChange={(e) => setForm({ ...form, razon_social: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Banco</label>
              <select
                value={form.banco_codigo}
                onChange={(e) => setForm({ ...form, banco_codigo: +e.target.value })}
              >
                {bancos.map((b) => (
                  <option key={b.codigo} value={b.codigo}>
                    {b.descripcion}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Tipo cuenta</label>
              <select
                value={form.tipo_cuenta}
                onChange={(e) => setForm({ ...form, tipo_cuenta: +e.target.value })}
              >
                {tiposCuenta.map((t) => (
                  <option key={t.codigo} value={t.codigo}>
                    {t.descripcion}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Número cuenta</label>
              <input
                value={form.numero_cuenta}
                onChange={(e) => setForm({ ...form, numero_cuenta: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
          </div>
          <div className="btn-group" style={{ marginTop: "1.25rem" }}>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Guardando…" : "Guardar"}
            </button>
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Proveedores() {
  const [items, setItems] = useState<Proveedor[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [q, setQ] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [bancos, setBancos] = useState<BancoCatalogo[]>([]);
  const [tiposId, setTiposId] = useState<CatalogoItem[]>([]);
  const [tiposCuenta, setTiposCuenta] = useState<CatalogoItem[]>([]);
  const [editing, setEditing] = useState<Proveedor | null | "new">(null);
  const [message, setMessage] = useState("");

  const loadCatalogos = useCallback(async () => {
    const [b, ti, tc] = await Promise.all([
      api.bancos(),
      api.tiposIdentificacion(),
      api.tiposCuenta(),
    ]);
    setBancos(b);
    setTiposId(ti);
    setTiposCuenta(tc);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.proveedores({ q: search, page, page_size: 20, activo: true });
      setItems(res.items);
      setTotal(res.total);
      setPages(res.pages);
    } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => {
    loadCatalogos();
  }, [loadCatalogos]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearch(q);
  };

  return (
    <>
      <h1 className="page-title">Proveedores</h1>
      <p className="page-subtitle">{total} proveedor(es) registrado(s)</p>

      {message && <div className="alert alert-success">{message}</div>}

      <div className="card">
        <div className="card-header">
          <form className="search-bar" onSubmit={handleSearch} style={{ flex: 1, margin: 0 }}>
            <input
              placeholder="Buscar por nombre, NIT o cuenta…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
            <button type="submit" className="btn btn-secondary">
              Buscar
            </button>
          </form>
          <button type="button" className="btn btn-primary" onClick={() => setEditing("new")}>
            + Nuevo
          </button>
        </div>

        {loading ? (
          <p className="empty-state">Cargando…</p>
        ) : items.length ? (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>NIT / ID</th>
                    <th>Razón social</th>
                    <th>Banco</th>
                    <th>Cuenta</th>
                    <th>Email</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((p) => (
                    <tr key={p.id}>
                      <td>
                        {p.identificacion}
                        {p.digito_verificacion != null ? `-${p.digito_verificacion}` : ""}
                      </td>
                      <td>{p.razon_social}</td>
                      <td>{p.banco?.descripcion ?? p.banco_codigo}</td>
                      <td>{p.numero_cuenta}</td>
                      <td>{p.email ?? "—"}</td>
                      <td>
                        <div className="btn-group">
                          <button
                            type="button"
                            className="btn btn-outline btn-sm"
                            onClick={() => setEditing(p)}
                          >
                            Editar
                          </button>
                        </div>
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
          <p className="empty-state">No hay proveedores. Crea uno o importa el Excel.</p>
        )}
      </div>

      {editing && bancos.length > 0 && (
        <ProveedorForm
          initial={editing === "new" ? null : editing}
          bancos={bancos}
          tiposId={tiposId}
          tiposCuenta={tiposCuenta}
          onSave={load}
          onClose={() => setEditing(null)}
        />
      )}
    </>
  );
}
