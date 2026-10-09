import { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";
import Callout from "../components/Callout.jsx";
import ChapterNav from "../components/ChapterNav.jsx";
import PageHead from "../components/PageHead.jsx";
import Stats from "../components/Stats.jsx";

const CHAPTERS = [
  { id: "score", label: "Score the messages" },
  { id: "tune", label: "Tune the threshold" },
  { id: "calibration", label: "Is it calibrated?" },
  { id: "how", label: "How it works" },
];
const pct = (p) => `${Math.round(p * 100)}%`;
const BINS = 5;

function confusion(items, t) {
  let tp = 0, fp = 0, fn = 0, tn = 0;
  items.forEach((i) => {
    const flagged = i.p_harmful >= t;
    if (flagged && i.harmful) tp++; else if (flagged) fp++; else if (i.harmful) fn++; else tn++;
  });
  return { tp, fp, fn, tn, precision: tp + fp ? tp / (tp + fp) : 1, recall: tp + fn ? tp / (tp + fn) : 1 };
}

function reliability(items) {
  const bins = Array.from({ length: BINS }, () => ({ n: 0, pred: 0, real: 0 }));
  items.forEach((i) => {
    const b = bins[Math.min(BINS - 1, Math.floor(i.p_harmful * BINS))];
    b.n++; b.pred += i.p_harmful; b.real += i.harmful ? 1 : 0;
  });
  const N = items.length;
  const out = bins.map((b, k) => ({ lo: k / BINS, hi: (k + 1) / BINS, n: b.n, pred: b.n ? b.pred / b.n : 0, real: b.n ? b.real / b.n : 0 }));
  const ece = out.reduce((a, b) => a + (b.n / N) * Math.abs(b.real - b.pred), 0);
  const brier = items.reduce((a, i) => a + (i.p_harmful - (i.harmful ? 1 : 0)) ** 2, 0) / N;
  return { bins: out, ece, brier };
}

function Chart({ bins }) {
  const S = 300, P = 46;
  const x = (v) => P + v * (S - P - 10), y = (v) => S - P - v * (S - P - 10);
  return (
    <svg className="rel" viewBox={`0 0 ${S} ${S}`} role="img" aria-label="Reliability chart: what Jev said against what happened">
      {[0, 0.5, 1].map((t) => (
        <g key={t}>
          <line className="rel-grid" x1={x(0)} x2={x(1)} y1={y(t)} y2={y(t)} />
          <text className="rel-t" x={P - 6} y={y(t) + 4} textAnchor="end">{t * 100}%</text>
          <text className="rel-t" x={x(t)} y={S - P + 16} textAnchor="middle">{t * 100}%</text>
        </g>
      ))}
      <line className="rel-diag" x1={x(0)} y1={y(0)} x2={x(1)} y2={y(1)} />
      <polyline className="rel-line" fill="none" points={bins.filter((b) => b.n).map((b) => `${x(b.pred)},${y(b.real)}`).join(" ")} />
      {bins.filter((b) => b.n).map((b) => (
        <g key={b.lo}>
          <circle className="rel-dot" cx={x(b.pred)} cy={y(b.real)} r={4 + Math.sqrt(b.n) * 1.6} />
          <text className="rel-n" x={x(b.pred)} y={y(b.real) + 3.5} textAnchor="middle">{b.n}</text>
        </g>
      ))}
      <text className="rel-t" x={S / 2} y={S - 4} textAnchor="middle">what Jev said</text>
      <text className="rel-t" x="9" y={S / 2} textAnchor="middle" transform={`rotate(-90 9 ${S / 2})`}>what happened</text>
    </svg>
  );
}

export default function ModerationLab({ usecase }) {
  const [guide, setGuide] = useState(null);
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [t, setT] = useState(50);
  const [filter, setFilter] = useState("all");
  const [mine, setMine] = useState("");
  const [mineResult, setMineResult] = useState(null);

  useEffect(() => { api.moderation.guide().then(setGuide).catch(() => {}); }, []);

  async function score() {
    setBusy(true); setError("");
    try { setData(await api.moderation.run()); } catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  async function tryMine() {
    setMineResult(null);
    try { setMineResult(await api.moderation.tryOne(mine)); } catch (e) { setMineResult({ error: e.message }); }
  }

  const items = data?.items ?? [];
  const m = useMemo(() => (items.length ? confusion(items, t / 100) : null), [items, t]);
  const rel = useMemo(() => (items.length ? reliability(items) : null), [items]);
  const rows = useMemo(() => {
    const sorted = [...items].sort((a, b) => b.p_harmful - a.p_harmful);
    const wrong = (i) => (i.p_harmful >= t / 100) !== i.harmful;
    return sorted.filter((i) => (filter === "errors" ? wrong(i) : filter === "tricky" ? i.hard : true));
  }, [items, t, filter]);

  return (
    <>
      {guide && <PageHead title={usecase.title} lead={guide.intro} roles={guide.roles} />}
      <ChapterNav chapters={CHAPTERS} />

      <section id="score" className="chapter">
        <h2>Score the messages</h2>
        <p className="lede">Seventy-six chat messages with our own labels: harmful or fine. Jev scores every one at the same time.</p>
        <div className="panel lab-start">
          <button className="primary" disabled={busy} onClick={score}>{busy ? "Scoring..." : data ? "Scored. Run again" : "Score all 76 messages"}</button>
          {data && <span className="muted small">{data.count} messages in {data.seconds} s, ${data.cost.toFixed(4)}{data.cached ? " (kept from an earlier run)" : ""}</span>}
          {error && <div className="error-text">{error}</div>}
        </div>
        {guide && <Callout title={guide.read_first.title} body={guide.read_first.body} />}
      </section>

      <section id="tune" className="chapter">
        <h2>Tune the threshold</h2>
        {!m && <p className="lede muted">Score the messages above, then drag the threshold here.</p>}
        {m && (
          <>
            <div className="panel">
              <label htmlFor="thr" className="thr-label">Flag a message when Jev is at least <b className="amber">{t}%</b> sure it is harmful</label>
              <input id="thr" type="range" min="1" max="99" value={t} onChange={(e) => setT(+e.target.value)} />
              <div className="thr-hint muted small"><span>catches more, more false alarms</span><span>fewer false alarms, more misses</span></div>
            </div>

            <Stats items={[
              { value: m.tp + m.fp, label: "flagged" },
              { value: m.fn, label: "harmful messages missed" },
              { value: m.fp, label: "false alarms" },
              { value: `${pct(m.precision)} / ${pct(m.recall)}`, label: "precision / recall" },
            ]} />

            <div className="cm">
              <div className="cm-h" /><div className="cm-h">Flagged</div><div className="cm-h">Let through</div>
              <div className="cm-h">Really harmful</div><div className="cm-c good">{m.tp}<span>caught</span></div><div className={`cm-c${m.fn ? " bad" : ""}`}>{m.fn}<span>missed</span></div>
              <div className="cm-h">Really fine</div><div className={`cm-c${m.fp ? " bad" : ""}`}>{m.fp}<span>false alarms</span></div><div className="cm-c good">{m.tn}<span>correctly passed</span></div>
            </div>

            <div className="toggle" role="group">
              {[["all", "All messages"], ["errors", "Mistakes only"], ["tricky", "Tricky ones"]].map(([k, label]) => (
                <button key={k} className={filter === k ? "on" : ""} onClick={() => setFilter(k)}>{label}</button>
              ))}
            </div>
            <div className="panel table-wrap">
              <table className="mod">
                <thead><tr><th>Message</th><th>Our label</th><th>Jev, harmful</th><th>At {t}%</th></tr></thead>
                <tbody>
                  {rows.map((i) => {
                    const flagged = i.p_harmful >= t / 100;
                    const err = flagged !== i.harmful;
                    return (
                      <tr key={i.id} className={err ? "err" : ""}>
                        <td>{i.text}</td>
                        <td>{i.harmful ? <span className="lbl bad">{i.kind}</span> : <span className="lbl">fine</span>}{i.ambiguous && <span className="lbl amb">contested</span>}</td>
                        <td className="pbar"><span><i style={{ width: `${i.p_harmful * 100}%` }} /></span>{pct(i.p_harmful)}</td>
                        <td>{flagged ? "Flagged" : "Passed"}{err && <b className="mistake"> ({flagged ? "false alarm" : "missed"})</b>}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {rows.length === 0 && <p className="muted">Nothing to show here at this threshold.</p>}

            <div className="panel">
              <h3>Try your own message</h3>
              <textarea rows={2} value={mine} onChange={(e) => setMine(e.target.value)} placeholder="Type a chat message..." />
              <button className="primary" disabled={!mine.trim()} onClick={tryMine}>Score it</button>
              {mineResult && !mineResult.error && (
                <p className="try-out"><b>{pct(mineResult.p_harmful)}</b> harmful, most likely kind: <b>{mineResult.kind_pred}</b> ({pct(mineResult.kind_pred_p)}).
                  At your threshold of {t}%, it would be <b>{mineResult.p_harmful >= t / 100 ? "flagged" : "let through"}</b>.</p>
              )}
              {mineResult?.error && <div className="error-text">{mineResult.error}</div>}
            </div>
          </>
        )}
      </section>

      <section id="calibration" className="chapter">
        <h2>Is the confidence honest?</h2>
        {guide && <p className="lede">{guide.calibration.what}</p>}
        {!rel && <p className="muted">Score the messages above to see the chart.</p>}
        {rel && guide && (
          <>
            <div className="rel-wrap">
              <Chart bins={rel.bins} />
              <div>
                <Stats items={[{ value: rel.ece.toFixed(3), label: "ECE" }, { value: rel.brier.toFixed(3), label: "Brier" }]} />
                <table className="rel-table">
                  <thead><tr><th>Jev said</th><th>Messages</th><th>Average said</th><th>Actually harmful</th></tr></thead>
                  <tbody>
                    {rel.bins.map((b) => (
                      <tr key={b.lo} className={b.n ? "" : "none"}>
                        <td>{pct(b.lo)} to {pct(b.hi)}</td><td>{b.n}</td><td>{b.n ? pct(b.pred) : "-"}</td><td>{b.n ? pct(b.real) : "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <p className="muted">{guide.calibration.ece}</p>
            <p className="muted">{guide.calibration.context}</p>
          </>
        )}
      </section>

      <section id="how" className="chapter">
        <h2>How it works</h2>
        {guide && (
          <>
            <dl className="terms">
              {guide.terms.map((x) => <div key={x.name}><dt>{x.name}</dt><dd>{x.line}</dd></div>)}
            </dl>
            <pre>{guide.code}</pre>
          </>
        )}
      </section>
    </>
  );
}
