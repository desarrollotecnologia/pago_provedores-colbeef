import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";
import { api } from "../api/client";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import type { Proveedor } from "../types";

interface ProveedorSearchProps {
  onSelect: (proveedor: Proveedor) => void;
  autoFocus?: boolean;
}

function highlightMatch(text: string, query: string) {
  if (!query.trim()) return text;
  const upper = text.toUpperCase();
  const q = query.trim().toUpperCase();
  const idx = upper.indexOf(q);
  if (idx === -1) return text;
  return (
    <>
      {text.slice(0, idx)}
      <mark className="search-highlight">{text.slice(idx, idx + q.length)}</mark>
      {text.slice(idx + q.length)}
    </>
  );
}

export default function ProveedorSearch({ onSelect, autoFocus = true }: ProveedorSearchProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Proveedor[]>([]);
  const [searching, setSearching] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const debouncedQuery = useDebouncedValue(query.trim(), 280);

  useEffect(() => {
    if (autoFocus) inputRef.current?.focus();
  }, [autoFocus]);

  useEffect(() => {
    if (debouncedQuery.length < 1) {
      setResults([]);
      setSearching(false);
      setActiveIndex(-1);
      return;
    }

    let cancelled = false;
    setSearching(true);

    api
      .proveedores({ q: debouncedQuery, page_size: 12, activo: true })
      .then((res) => {
        if (!cancelled) {
          setResults(res.items);
          setActiveIndex(res.items.length ? 0 : -1);
        }
      })
      .catch(() => {
        if (!cancelled) setResults([]);
      })
      .finally(() => {
        if (!cancelled) setSearching(false);
      });

    return () => {
      cancelled = true;
    };
  }, [debouncedQuery]);

  const select = useCallback(
    (p: Proveedor) => {
      onSelect(p);
      setQuery("");
      setResults([]);
      setActiveIndex(-1);
    },
    [onSelect]
  );

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (!results.length) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && activeIndex >= 0) {
      e.preventDefault();
      select(results[activeIndex]);
    }
  };

  const showHint = query.trim().length === 0;
  const showNoResults = debouncedQuery.length >= 1 && !searching && results.length === 0;
  const showResults = debouncedQuery.length >= 1 && results.length > 0;

  return (
    <div className="proveedor-search">
      <label className="proveedor-search-label" htmlFor="proveedor-search-input">
        Buscar proveedor
      </label>
      <div className="proveedor-search-input-wrap">
        <span className="proveedor-search-icon" aria-hidden>
          ⌕
        </span>
        <input
          id="proveedor-search-input"
          ref={inputRef}
          type="search"
          autoComplete="off"
          spellCheck={false}
          placeholder="Nombre, NIT o número de cuenta…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        {searching && <span className="proveedor-search-spinner" aria-hidden />}
      </div>

      <p className="proveedor-search-hint">
        Los resultados aparecen al escribir. Use ↑ ↓ y Enter para seleccionar.
      </p>

      {showHint && (
        <div className="proveedor-search-empty">
          Escriba una o dos letras del nombre, el NIT o la cuenta bancaria.
        </div>
      )}

      {searching && debouncedQuery.length >= 1 && (
        <div className="proveedor-search-loading">Buscando coincidencias…</div>
      )}

      {showNoResults && (
        <div className="proveedor-search-empty">
          No se encontró ningún proveedor para «{debouncedQuery}».
        </div>
      )}

      {showResults && (
        <ul className="proveedor-search-results" role="listbox">
          {results.map((p, i) => (
            <li key={p.id} role="option" aria-selected={i === activeIndex}>
              <button
                type="button"
                className={`proveedor-search-item${i === activeIndex ? " active" : ""}`}
                onClick={() => select(p)}
                onMouseEnter={() => setActiveIndex(i)}
              >
                <span className="proveedor-search-name">
                  {highlightMatch(p.razon_social, debouncedQuery)}
                </span>
                <span className="proveedor-search-meta">
                  <span>NIT {highlightMatch(p.identificacion, debouncedQuery)}</span>
                  {p.banco?.descripcion && <span>{p.banco.descripcion}</span>}
                  {p.numero_cuenta && (
                    <span>Cta. {highlightMatch(p.numero_cuenta, debouncedQuery)}</span>
                  )}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
