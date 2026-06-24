import { LogoPagoIcon } from "./BrandIcons";

interface BrandLogoBoxProps {
  size?: "sm" | "md";
}

export default function BrandLogoBox({ size = "md" }: BrandLogoBoxProps) {
  const dim = size === "sm" ? 44 : 56;
  const icon = size === "sm" ? 36 : 44;
  return (
    <div className="brand-logo-box" style={{ width: dim, height: dim }}>
      <LogoPagoIcon size={icon} />
    </div>
  );
}
