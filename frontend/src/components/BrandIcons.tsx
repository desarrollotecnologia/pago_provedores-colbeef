/** Iconos de marca — calendario + pagos (estilo Colbeef tesorería). */

export function LogoPagoIcon({ size = 40 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 80 72"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      {/* Calendario */}
      <rect x="6" y="16" width="42" height="38" rx="4" fill="#F4F4F5" />
      <rect x="6" y="16" width="42" height="13" rx="4" fill="#E63946" />
      <rect x="6" y="25" width="42" height="4" fill="#E63946" />
      <rect x="14" y="11" width="5" height="8" rx="2" fill="#FFB703" />
      <rect x="35" y="11" width="5" height="8" rx="2" fill="#FFB703" />
      <text
        x="12"
        y="36"
        fill="#E91E63"
        fontSize="11"
        fontWeight="bold"
        fontFamily="Arial, sans-serif"
      >
        MAY
      </text>
      <rect x="34" y="30" width="4" height="2" rx="1" fill="#B0B0B0" />
      <rect x="40" y="30" width="4" height="2" rx="1" fill="#B0B0B0" />
      {[0, 1, 2].map((row) =>
        [0, 1, 2, 3].map((col) => (
          <rect
            key={`${row}-${col}`}
            x={12 + col * 8}
            y={40 + row * 6}
            width="5"
            height="3"
            rx="1.5"
            fill="#C4C4C4"
          />
        ))
      )}

      {/* Moneda */}
      <circle cx="58" cy="30" r="14" fill="#FFB703" />
      <circle cx="58" cy="30" r="11" fill="#FFC933" />
      <text
        x="58"
        y="35"
        textAnchor="middle"
        fill="#FFF8E1"
        fontSize="14"
        fontWeight="bold"
        fontFamily="Arial, sans-serif"
      >
        $
      </text>

      {/* Billetes */}
      <rect x="38" y="46" width="8" height="22" rx="2" fill="#3A5BA0" />
      <rect x="44" y="44" width="8" height="22" rx="2" fill="#4361EE" />
      <rect x="30" y="42" width="28" height="18" rx="3" fill="#4895EF" />
      <circle cx="44" cy="51" r="5" fill="#fff" opacity="0.95" />
      <rect x="33" y="45" width="5" height="3" rx="1" fill="#3B6FD4" />
      <rect x="50" y="45" width="5" height="3" rx="1" fill="#3B6FD4" />
    </svg>
  );
}

export function HandPayIcon({ size = 36 }: { size?: number }) {
  return <LogoPagoIcon size={size} />;
}
