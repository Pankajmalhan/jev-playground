// The top of a playground page: title, one-line lead, and an optional row of roles.
export default function PageHead({ title, lead, roles }) {
  return (
    <header className="page-head">
      <h1>{title}</h1>
      {lead && <p className="lead">{lead}</p>}
      {roles && (
        <div className="roles">
          {roles.map((r) => (
            <div key={r.name} className={`role${r.jev ? " jev" : ""}`}>
              <span className="lane-role">{r.role}</span>
              <b>{r.name}</b>
              <span>{r.line}</span>
            </div>
          ))}
        </div>
      )}
    </header>
  );
}
