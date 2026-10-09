import { useState } from "react";
import { api } from "../api.js";

// Why a probability beats a label: answer every sample message once, then drag
// a threshold and watch messages move between "handled automatically" and
// "a person decides".
export default function ConfidenceLab({ calibration }) {
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [threshold, setThreshold] = useState(60);

  async function load() {
    setBusy(true);
    setError("");
    try {
      setData(await api.whatIsJev.batch());
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  const items = data ? [...data.items].sort((a, b) => a.confidence - b.confidence) : [];
  const auto = items.filter((i) => i.confidence * 100 >= threshold).length;

  return (
    <div>
      <blockquote>{calibration.quote}</blockquote>
      <p className="muted lede">{calibration.body}</p>

      {!data ? (
        <div className="panel lab-start">
          <button className="primary" disabled={busy} onClick={load}>
            {busy ? "Asking Jev..." : "Answer all the sample messages"}
          </button>
          <span className="muted small">One call per message, all at once. It costs a fraction of a cent.</span>
          {error && <div className="error-text">{error}</div>}
        </div>
      ) : (
        <div className="panel">
          <div className="lab-head">
            <label htmlFor="threshold">
              A person decides when Jev is less than <b className="amber">{threshold}%</b> sure of the team
            </label>
            <input id="threshold" type="range" min="50" max="100" value={threshold} onChange={(e) => setThreshold(+e.target.value)} />
          </div>
          <div className="lab-score">
            <span><b>{auto}</b> handled automatically</span>
            <span><b>{items.length - auto}</b> sent to a person</span>
            <span className="muted small">{data.calls} calls in {data.wall_seconds.toFixed(2)} s, ${data.cost.toFixed(4)} in all</span>
          </div>
          <ul className="lab-rows">
            {items.map((i) => {
              const ok = i.confidence * 100 >= threshold;
              return (
                <li key={i.id} className={ok ? "ok" : "person"}>
                  <span className="lab-title">{i.title}</span>
                  <span className="lab-dept">{i.department}</span>
                  <span className="lab-bar">
                    <span className="lab-fill" style={{ width: `${i.confidence * 100}%` }} />
                    <span className="lab-line" style={{ left: `${threshold}%` }} />
                  </span>
                  <span className="lab-pct">{(i.confidence * 100).toFixed(0)}%</span>
                  <span className="lab-verdict">{ok ? "Automatic" : "A person decides"}</span>
                </li>
              );
            })}
          </ul>
          <p className="muted small">Each bar is how sure Jev was about the team. The demo above uses a threshold of 60%. A very short message can still get a confident answer, so check calibration against your own data before trusting a threshold.</p>
        </div>
      )}
    </div>
  );
}
