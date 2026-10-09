// A small flow diagram for a playground card: what goes in, what does the work,
// what comes out. Drawn from the `diagram` data in the use case's meta.py.
export default function MiniFlow({ rows }) {
  return (
    <div className="mf" role="img" aria-label={rows.map((r) => (r.label ? `${r.label}: ` : "") + r.nodes.map((n) => n.text).join(", then ")).join(". ")}>
      {rows.map((row, i) => (
        <div key={i}>
          {row.label && <div className="mf-label">{row.label}</div>}
          <div className="mf-row">
            {row.nodes.map((n, j) => (
              <span key={j} className="mf-cell">
                {j > 0 && <span className="mf-link" />}
                <span className={`mf-node ${n.kind}`}>
                  <b>{n.text}</b>
                  {n.note && <i>{n.note}</i>}
                </span>
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
