/** Iconos de marca embebidos — no dependen de archivos externos en el servidor. */

export function LogoPagoIcon({ size = 40 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 80 56"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <rect x="4" y="8" width="52" height="36" rx="4" fill="#dcfce7" stroke="#1a6b42" strokeWidth="2" />
      <circle cx="30" cy="26" r="10" fill="#1a6b42" />
      <text x="30" y="30" textAnchor="middle" fill="#fff" fontSize="12" fontWeight="bold" fontFamily="Arial,sans-serif">
        $
      </text>
      <rect x="36" y="4" width="40" height="28" rx="4" fill="#3b82f6" transform="rotate(12 56 18)" />
      <rect x="44" y="10" width="20" height="4" rx="1" fill="#93c5fd" transform="rotate(12 56 18)" />
    </svg>
  );
}

export function HandPayIcon({ size = 36 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        d="M14 36c0-10 8-18 18-18s18 8 18 18"
        stroke="#f0c9a8"
        strokeWidth="5"
        strokeLinecap="round"
      />
      <rect x="20" y="18" width="30" height="20" rx="3" fill="#3b82f6" />
      <rect x="24" y="22" width="9" height="7" rx="1" fill="#fbbf24" />
      <rect x="16" y="26" width="26" height="18" rx="2" fill="#92400e" />
      <rect x="12" y="28" width="24" height="16" rx="2" fill="#dc2626" />
      <rect x="38" y="4" width="18" height="52" rx="4" fill="#16a34a" />
    </svg>
  );
}
