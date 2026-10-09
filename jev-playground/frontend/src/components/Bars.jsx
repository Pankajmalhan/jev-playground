// Horizontal probability bars for one Jev answer: { label: probability }.
export default function Bars({ options, winner }) {
  const rows = Object.entries(options).sort((a, b) => b[1] - a[1]);
  return (
    <div className="bars">
      {rows.map(([label, p]) => (
        <div className={`bar-row${label === winner ? " win" : ""}`} key={label}>
          <span className="bar-label">{label}</span>
          <span className="bar-track">
            <span className="bar-fill" style={{ width: `${Math.round(p * 100)}%` }} />
          </span>
          <span className="bar-pct">{(p * 100).toFixed(0)}%</span>
        </div>
      ))}
    </div>
  );
}
