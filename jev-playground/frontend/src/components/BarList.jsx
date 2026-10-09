// A plain list of horizontal bars: [{ label, value, text }]. `value` is 0 to 1; `text` is shown at the end.
export default function BarList({ items, tone }) {
  return (
    <div className={`blist${tone ? ` tone-${tone}` : ""}`}>
      {items.map((it) => (
        <div className="bl-row" key={it.label}>
          <span className="bl-label">{it.label}</span>
          <span className="bl-track"><span className="bl-fill" style={{ width: `${Math.max(0, Math.min(1, it.value)) * 100}%` }} /></span>
          <span className="bl-text">{it.text}</span>
        </div>
      ))}
    </div>
  );
}
