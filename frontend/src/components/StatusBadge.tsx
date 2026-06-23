import { statusClass } from "../utils/format";

export default function StatusBadge({ estado }: { estado: string }) {
  return <span className={statusClass(estado)}>{estado.replace(/_/g, " ")}</span>;
}
