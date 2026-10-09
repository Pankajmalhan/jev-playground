// A strip of numbers: [{ value, label }].
export default function Stats({ items }) {
  return (
    <div className="stats">
      {items.map((s) => (
        <div key={s.label}><b>{s.value}</b><span>{s.label}</span></div>
      ))}
    </div>
  );
}
