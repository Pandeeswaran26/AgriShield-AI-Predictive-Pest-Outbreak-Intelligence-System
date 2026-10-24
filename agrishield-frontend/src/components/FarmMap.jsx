import { useState, useRef } from "react";

/**
 * FarmMap — Interactive field surveillance map using SVG canvas.
 * Displays each plant/field as a risk-coded marker on a grid canvas.
 * Clicking a marker reveals a quick-view modal with crop context.
 */

const RISK_COLORS = {
  High: { bg: "#ef4444", glow: "rgba(239,68,68,0.4)", icon: "🔴", label: "High Risk", text: "#fff" },
  Medium: { bg: "#f59e0b", glow: "rgba(245,158,11,0.4)", icon: "🟡", label: "Medium Risk", text: "#1a1a1a" },
  Low: { bg: "#22c55e", glow: "rgba(34,197,94,0.4)", icon: "🟢", label: "Low Risk", text: "#fff" },
  Unknown: { bg: "#6b7280", glow: "rgba(107,114,128,0.4)", icon: "⚪", label: "No Data", text: "#fff" },
};

function getRiskKey(riskLevel) {
  if (!riskLevel) return "Unknown";
  const r = riskLevel.toLowerCase();
  if (r.includes("high")) return "High";
  if (r.includes("med")) return "Medium";
  if (r.includes("low")) return "Low";
  return "Unknown";
}

// Deterministic pseudo-random scatter from plant id
function getFieldPosition(id) {
  const seed = (id * 2654435761) >>> 0;
  const x = 8 + (((seed & 0xFFF) / 0xFFF) * 84);
  const y = 8 + ((((seed >> 12) & 0xFFF) / 0xFFF) * 80);
  return { x, y };
}

export default function FarmMap({ plants = [], onFieldClick }) {
  const [selected, setSelected] = useState(null);
  const svgRef = useRef(null);

  const handleMarkerClick = (plant) => {
    setSelected(plant);
    if (onFieldClick) onFieldClick(plant);
  };

  const handleClose = () => setSelected(null);

  if (!plants.length) {
    return (
      <div className="farm-map-empty">
        <div className="farm-map-empty-icon">🗺️</div>
        <p>No fields registered yet.</p>
        <span>Add your first field to see it on the surveillance map.</span>
      </div>
    );
  }

  return (
    <div className="farm-map-wrapper">
      <div className="farm-map-header">
        <span className="farm-map-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
          Farm Surveillance Map
        </span>
        <div className="farm-map-legend">
          {Object.entries(RISK_COLORS).filter(([k]) => k !== "Unknown").map(([k, v]) => (
            <span key={k} className="farm-map-legend-item">
              <span style={{ background: v.bg, width: 10, height: 10, borderRadius: "50%", display: "inline-block", marginRight: 4 }} />
              {v.label}
            </span>
          ))}
        </div>
      </div>

      <div className="farm-map-canvas-wrapper">
        <svg
          ref={svgRef}
          viewBox="0 0 100 100"
          className="farm-map-svg"
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Grid lines */}
          {[20, 40, 60, 80].map(v => (
            <g key={v}>
              <line x1={v} y1={0} x2={v} y2={100} stroke="rgba(255,255,255,0.05)" strokeWidth="0.3" />
              <line x1={0} y1={v} x2={100} y2={v} stroke="rgba(255,255,255,0.05)" strokeWidth="0.3" />
            </g>
          ))}

          {/* Field markers */}
          {plants.map((plant, i) => {
            const riskKey = getRiskKey(plant.last_risk_level);
            const color = RISK_COLORS[riskKey];
            const pos = getFieldPosition(plant.id || i, plants.length);
            const isSelected = selected?.id === plant.id;

            return (
              <g key={plant.id || i} style={{ cursor: "pointer" }} onClick={() => handleMarkerClick(plant)}>
                {/* Pulse ring for high risk */}
                {riskKey === "High" && (
                  <circle cx={pos.x} cy={pos.y} r="4.5" fill="none" stroke={color.bg} strokeWidth="0.8" opacity="0.5">
                    <animate attributeName="r" values="4.5;7;4.5" dur="2s" repeatCount="indefinite" />
                    <animate attributeName="opacity" values="0.5;0;0.5" dur="2s" repeatCount="indefinite" />
                  </circle>
                )}
                {/* Marker circle */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={isSelected ? 4.2 : 3.5}
                  fill={color.bg}
                  stroke={isSelected ? "#fff" : "rgba(255,255,255,0.3)"}
                  strokeWidth={isSelected ? 0.8 : 0.4}
                  style={{ filter: `drop-shadow(0 0 3px ${color.glow})` }}
                />
                {/* Field name label */}
                <text
                  x={pos.x}
                  y={pos.y + 6.5}
                  textAnchor="middle"
                  fontSize="2.8"
                  fill="rgba(255,255,255,0.7)"
                  fontFamily="sans-serif"
                >
                  {(plant.name || plant.field_name || `Field ${plant.id}`).substring(0, 12)}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Quick-view Modal */}
        {selected && (
          <div className="farm-map-modal" onClick={handleClose}>
            <div className="farm-map-modal-card" onClick={e => e.stopPropagation()}>
              <button className="farm-map-modal-close" onClick={handleClose}>✕</button>

              <div className="farm-map-modal-badge" style={{ background: RISK_COLORS[getRiskKey(selected.last_risk_level)].bg }}>
                {RISK_COLORS[getRiskKey(selected.last_risk_level)].icon} {RISK_COLORS[getRiskKey(selected.last_risk_level)].label}
              </div>

              <h3 className="farm-map-modal-title">
                {selected.name || selected.field_name || `Field ${selected.id}`}
              </h3>

              <div className="farm-map-modal-grid">
                <div className="farm-map-modal-row">
                  <span className="farm-map-modal-label">🌾 Crop</span>
                  <span className="farm-map-modal-value">{selected.crop_name || selected.crop || "—"}</span>
                </div>
                <div className="farm-map-modal-row">
                  <span className="farm-map-modal-label">📅 Growth Stage</span>
                  <span className="farm-map-modal-value">{selected.growth_stage || selected.last_health_status || "—"}</span>
                </div>
                <div className="farm-map-modal-row">
                  <span className="farm-map-modal-label">🌡 Soil Type</span>
                  <span className="farm-map-modal-value">{selected.soil_type || "—"}</span>
                </div>
                {selected.field_size && (
                  <div className="farm-map-modal-row">
                    <span className="farm-map-modal-label">📐 Area</span>
                    <span className="farm-map-modal-value">{selected.field_size} ha</span>
                  </div>
                )}
                {selected.last_recommended_action && (
                  <div className="farm-map-modal-action">
                    <span className="farm-map-modal-label">💡 Top Action</span>
                    <p className="farm-map-modal-action-text">{selected.last_recommended_action}</p>
                  </div>
                )}
              </div>

              <button
                className="farm-map-modal-btn"
                onClick={() => { handleClose(); if (onFieldClick) onFieldClick(selected); }}
              >
                View Full Assessment →
              </button>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .farm-map-wrapper {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 16px;
          overflow: hidden;
        }
        .farm-map-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 20px;
          border-bottom: 1px solid rgba(255,255,255,0.07);
          flex-wrap: wrap;
          gap: 8px;
        }
        .farm-map-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 600;
          color: #e2e8f0;
        }
        .farm-map-legend {
          display: flex;
          gap: 14px;
          flex-wrap: wrap;
        }
        .farm-map-legend-item {
          display: flex;
          align-items: center;
          font-size: 11px;
          color: #94a3b8;
        }
        .farm-map-canvas-wrapper {
          position: relative;
          background: radial-gradient(ellipse at 30% 40%, rgba(16,185,129,0.04) 0%, transparent 60%),
                      radial-gradient(ellipse at 70% 60%, rgba(99,102,241,0.04) 0%, transparent 60%),
                      #0f172a;
          min-height: 280px;
        }
        .farm-map-svg {
          width: 100%;
          height: 280px;
          display: block;
        }
        .farm-map-empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 48px 24px;
          gap: 8px;
          color: #64748b;
          text-align: center;
          background: rgba(255,255,255,0.02);
          border-radius: 16px;
          border: 1px solid rgba(255,255,255,0.06);
        }
        .farm-map-empty-icon { font-size: 36px; }
        .farm-map-empty p { font-size: 15px; font-weight: 500; color: #94a3b8; margin: 0; }
        .farm-map-empty span { font-size: 12px; }
        .farm-map-modal {
          position: absolute;
          inset: 0;
          background: rgba(0,0,0,0.6);
          backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 50;
          animation: fadeIn 0.15s ease;
        }
        @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
        .farm-map-modal-card {
          background: #1e293b;
          border: 1px solid rgba(255,255,255,0.12);
          border-radius: 14px;
          padding: 20px;
          width: min(340px, 90%);
          position: relative;
          animation: slideUp 0.18s ease;
        }
        @keyframes slideUp { from { transform: translateY(10px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .farm-map-modal-close {
          position: absolute;
          top: 12px;
          right: 14px;
          background: none;
          border: none;
          color: #94a3b8;
          cursor: pointer;
          font-size: 16px;
        }
        .farm-map-modal-badge {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          font-size: 11px;
          font-weight: 700;
          color: #fff;
          padding: 3px 10px;
          border-radius: 20px;
          margin-bottom: 10px;
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .farm-map-modal-title {
          font-size: 17px;
          font-weight: 700;
          color: #f1f5f9;
          margin: 0 0 14px;
        }
        .farm-map-modal-grid { display: flex; flex-direction: column; gap: 8px; }
        .farm-map-modal-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 6px 0;
          border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .farm-map-modal-label { font-size: 12px; color: #94a3b8; }
        .farm-map-modal-value { font-size: 12px; font-weight: 600; color: #e2e8f0; }
        .farm-map-modal-action { margin-top: 6px; }
        .farm-map-modal-action-text { font-size: 12px; color: #86efac; margin: 4px 0 0; line-height: 1.5; }
        .farm-map-modal-btn {
          width: 100%;
          margin-top: 16px;
          padding: 9px 0;
          background: linear-gradient(135deg, #16a34a, #15803d);
          border: none;
          border-radius: 8px;
          color: #fff;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: opacity 0.2s;
        }
        .farm-map-modal-btn:hover { opacity: 0.88; }
      `}</style>
    </div>
  );
}
