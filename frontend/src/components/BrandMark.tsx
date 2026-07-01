type BrandTone = "sidebar" | "topbar" | "login";

export function BrandEyebrow({ className = "" }: { className?: string }) {
  return <span className={`brand-eyebrow ${className}`.trim()}>Sistema de pagos</span>;
}

export function BrandName({ tone = "topbar" }: { tone?: BrandTone }) {
  return (
    <span className={`brand-name brand-name--${tone}`}>
      PROVEEDORES - <span className="brand-colbeef">COLBEEF</span>
    </span>
  );
}
