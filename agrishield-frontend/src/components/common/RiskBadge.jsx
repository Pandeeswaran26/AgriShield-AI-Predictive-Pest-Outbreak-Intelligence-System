import { riskBadgeClasses } from "../../utils/risk";

export default function RiskBadge({ level }) {
  return (
    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${riskBadgeClasses(level)}`}>
      {level}
    </span>
  );
}
