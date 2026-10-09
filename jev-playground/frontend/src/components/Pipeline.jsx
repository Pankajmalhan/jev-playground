import { useEffect, useRef, useState } from "react";

const reduced = () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

// The backend, drawn as stages you can click. After a run, every stage shows
// the real data that passed through it and how long it really took.
export default function Pipeline({ steps, trace, roundTrip }) {
  const [sel, setSel] = useState(3);
  const [lit, setLit] = useState(-1);
  const timer = useRef(null);
  const byId = Object.fromEntries((trace || []).map((t) => [t.id, t]));

  function play() {
    clearInterval(timer.current);
    let i = 0;
    setSel(0);
    setLit(0);
    timer.current = setInterval(() => {
      i += 1;
      if (i >= steps.length) {
        clearInterval(timer.current);
        setLit(-1);
        setSel(Math.max(steps.findIndex((s) => s.highlight), 0)); // end on the Jev stage
        return;
      }
      setSel(i);
      setLit(i);
    }, 850);
  }

  // A new run replays the journey once, unless the reader prefers less motion.
  useEffect(() => {
    if (trace && !reduced()) play();
    return () => clearInterval(timer.current);
  }, [trace]);

  const step = steps[sel];
  const t = byId[step.id];
  const timed = steps.filter((s) => byId[s.id]?.ms != null);
  const total = timed.reduce((a, s) => a + byId[s.id].ms, 0);
  const jevMs = byId.jev?.ms ?? 0;

  return (
    <div className="pipe-wrap">
      <div className="pipe-bar">
        <button className="ghost" onClick={play}>{trace ? "Replay this run" : "Play the journey"}</button>
        <span className="muted small">
          {trace ? "Click any stage to see the data that went through it." : "Run a message above and every stage fills with its real data."}
        </span>
      </div>

      <ol className="pipe">
        {steps.map((s, i) => (
          <li key={s.id}>
            {i > 0 && <span className={`link${lit >= i ? " lit" : ""}`} aria-hidden="true" />}
            <button
              className={`node${sel === i ? " sel" : ""}${lit >= i ? " lit" : ""}${s.highlight ? " hot" : ""}${s.tag ? " plain" : ""}`}
              aria-pressed={sel === i}
              onClick={() => { clearInterval(timer.current); setLit(-1); setSel(i); }}
            >
              <span className="node-n">{i + 1}</span>
              <span className="node-label">{s.label}</span>
              <span className="node-file">{s.file}</span>
            </button>
          </li>
        ))}
      </ol>

      <div className="stage">
        <div>
          <div className="step-meta">
            <span className={`layer${step.highlight ? " amber" : ""}`}>{step.layer}</span>
            <span className="file">{step.file}</span>
            {step.tag && <span className="tag">{step.tag}</span>}
          </div>
          <h3>{step.title}</h3>
          <p className="muted">{step.detail}</p>
          {t?.ms != null && (
            <p className="took">This stage took <b>{t.ms < 1 ? "under 1 ms" : `${t.ms.toLocaleString()} ms`}</b>.</p>
          )}
        </div>
        <div>
          <div className="code-label">{step.data_note}</div>
          {t ? <pre>{JSON.stringify(t.data, null, 2)}</pre> : <pre className="empty">Run a message to see the real data here.</pre>}
        </div>
      </div>

      {step.code && (
        <details className="code-more">
          <summary>Show the code for this stage</summary>
          <pre>{step.code}</pre>
        </details>
      )}

      {trace && (
        <div className="timing">
          <h3>Where the time went</h3>
          <div className="timebar" role="img" aria-label={`The Jev call took ${jevMs} of ${total.toFixed(0)} milliseconds on the server`}>
            {timed.map((s) => (
              <span
                key={s.id}
                className={`seg${s.id === "jev" ? " jev" : ""}`}
                style={{ flexGrow: Math.max(byId[s.id].ms, 0.0001) }}
                title={`${s.label}: ${byId[s.id].ms} ms`}
              />
            ))}
          </div>
          <p className="muted">
            The Jev call is <b className="amber">{jevMs / total > 0.999 ? "over 99.9%" : `${((jevMs / total) * 100).toFixed(1)}%`}</b> of the {Math.round(total).toLocaleString()} ms
            the server spent. Everything your own code does (building the request, flattening, the rules, logging) adds up to{" "}
            {(total - jevMs).toFixed(1)} ms.
            {roundTrip != null && <> Your browser waited {Math.round(roundTrip).toLocaleString()} ms in all.</>}
          </p>
        </div>
      )}
    </div>
  );
}
