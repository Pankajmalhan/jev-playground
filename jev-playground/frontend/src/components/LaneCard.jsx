import Bars from "./Bars.jsx";

const SHORT = { department: "Team", urgency: "Urgency", refund_due: "Refund owed?" };

// One lane of the race: waiting, running with a live clock, or finished.
export default function LaneCard({ role, lane, elapsed, expected }) {
  const { status, result, error } = lane;

  return (
    <article className={`lane ${role.id}`}>
      <header>
        <h3>{role.name}</h3>
        <span className="lane-role">{role.role}</span>
      </header>

      {status === "idle" && (
        <>
          <p className="muted">{role.line}</p>
          <ul className="lane-facts">{role.facts.map((f) => <li key={f}>{f}</li>)}</ul>
        </>
      )}

      {status === "running" && (
        <div className="running">
          <span className="timer">{elapsed.toFixed(1)} s</span>
          <span className="muted small"><i className="pulse" /> working...</span>
        </div>
      )}

      {status === "error" && <div className="error-text">{error}</div>}

      {status === "done" && (
        <>
          <div className="metrics">
            <div><b>{result.seconds.toFixed(2)} s</b><span>time</span></div>
            <div><b>{result.calls}</b><span>{result.calls === 1 ? "model call" : "model calls"}</span></div>
            <div><b>${result.cost.toFixed(5)}</b><span>cost</span></div>
          </div>

          <ul className="lane-answers">
            {result.answers.map((a) => {
              const want = expected?.[a.key];
              const mark = want === undefined ? null : want === a.value ? "ok" : "bad";
              return (
                <li key={a.key}>
                  <div className="ans">
                    <span className="ans-q">{SHORT[a.key] || a.key}</span>
                    <span className="ans-v">{a.value}</span>
                    <span className="ans-c">{(a.confidence * 100).toFixed(0)}%</span>
                    {mark && (
                      <span className={`mark ${mark}`} title={`Answer key: ${want}`}>{mark === "ok" ? "Correct" : `Expected ${want}`}</span>
                    )}
                  </div>
                  {a.options && (
                    <details className="opt">
                      <summary>every option</summary>
                      <Bars options={a.options} winner={a.value} />
                    </details>
                  )}
                </li>
              );
            })}
          </ul>
          <p className="conf-note">
            {role.id === "jev" ? "Percentages are Jev's probabilities." : "Percentages are what the model says about itself."}
          </p>

          {result.reason && <blockquote className="reason">{result.reason}</blockquote>}

          <div className="code-label">What it did</div>
          <ol className="did">
            {result.steps.map((s, i) => (
              <li key={i} className={s.type}>
                <span className="did-kind">{s.type === "model" ? "Model" : s.type === "tool" ? "Tool" : "Code"}</span>
                <span className="did-note">{s.note}</span>
                <span className="did-ms">{s.ms >= 1 ? `${Math.round(s.ms)} ms` : "under 1 ms"}</span>
                {s.result && <code className="did-result">{JSON.stringify(s.result)}</code>}
              </li>
            ))}
          </ol>
        </>
      )}
    </article>
  );
}
