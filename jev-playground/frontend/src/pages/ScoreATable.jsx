import { useEffect, useState } from "react";
import { api } from "../api.js";
import BarList from "../components/BarList.jsx";
import Callout from "../components/Callout.jsx";
import ChapterNav from "../components/ChapterNav.jsx";
import PageHead from "../components/PageHead.jsx";
import Stats from "../components/Stats.jsx";

const CHAPTERS = [
  { id: "run", label: "Run it" },
  { id: "dash", label: "The dashboard" },
  { id: "cost", label: "What it costs" },
  { id: "how", label: "How it works" },
];
const SCALES = [1_000, 100_000, 1_000_000, 50_000_000];
const money = (v) => (v < 0.01 ? `$${v.toFixed(4)}` : v < 100 ? `$${v.toFixed(2)}` : `$${Math.round(v).toLocaleString()}`);
const pct = (p) => `${Math.round(p * 100)}%`;

function duration(s) {
  if (s < 90) return `${Math.round(s)} seconds`;
  if (s < 5400) return `${Math.round(s / 60)} minutes`;
  if (s < 172800) return `${(s / 3600).toFixed(1)} hours`;
  return `${(s / 86400).toFixed(1)} days`;
}

export default function ScoreATable({ usecase }) {
  const [guide, setGuide] = useState(null);
  const [size, setSize] = useState(200);
  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => { api.table.guide().then(setGuide).catch(() => {}); }, []);

  async function run() {
    setStatus("running"); setError(""); setSummary(null); setProgress({ done: 0, total: size, elapsed: 0, rows_per_second: 0, cost: 0 });
    try {
      await api.table.run(size, (e) => {
        if (e.type === "progress") setProgress(e);
        if (e.type === "done") { setSummary(e.summary); setStatus("done"); }
        if (e.type === "error") { setError(e.message); setStatus("idle"); }
      });
    } catch (err) {
      setError(err.message); setStatus("idle");
    }
  }

  const s = summary;
  const running = status === "running";
  const maxMatrix = s ? Math.max(1, ...Object.values(s.matrix).flatMap((m) => Object.values(m))) : 1;
  const questionTokens = s ? Math.max(0, s.avg_tokens - s.avg_review_tokens) : 0;

  return (
    <>
      {guide && <PageHead title={usecase.title} lead={guide.intro} roles={guide.roles} />}
      <ChapterNav chapters={CHAPTERS} />

      <section id="run" className="chapter">
        <h2>Run it</h2>
        <p className="lede">Pick how many reviews to score. Jev answers {guide?.questions.length ?? 4} questions about each one, many at a time.</p>
        <div className="panel">
          <div className="code-label">Reviews to score</div>
          <div className="toggle" role="group">
            {(guide?.sizes ?? [50, 200, 500, 1000]).map((n) => (
              <button key={n} className={size === n ? "on" : ""} disabled={running} onClick={() => setSize(n)}>{n.toLocaleString()}</button>
            ))}
          </div>
          <p className="muted small">
            About {money(size * (guide?.typical_cost_per_row ?? 0.00003))} for {size.toLocaleString()} rows, based on a typical run.
          </p>
          <button className="primary" disabled={running} onClick={run}>{running ? "Scoring..." : "Score the table"}</button>
          {error && <div className="error-text">{error}</div>}

          {progress && (running || status === "done") && (
            <div className="prog">
              <div className="prog-track"><span style={{ width: `${(progress.done / progress.total) * 100}%` }} /></div>
              <div className="prog-text">
                <b>{progress.done.toLocaleString()}</b> of {progress.total.toLocaleString()} rows
                <span className="muted"> · {progress.elapsed.toFixed(1)} s · {progress.rows_per_second} rows per second · {money(progress.cost)}</span>
              </div>
            </div>
          )}
        </div>
        {guide && <Callout title={guide.read_first.title} body={guide.read_first.body} />}
      </section>

      <section id="dash" className="chapter">
        <h2>The dashboard</h2>
        {!s && <p className="lede muted">Run the table above and the dashboard fills in here.</p>}
        {s && (
          <>
            <Stats items={[
              { value: s.rows.toLocaleString(), label: "rows scored" },
              { value: `${s.seconds.toFixed(1)}s`, label: "whole run" },
              { value: `${s.rows_per_second}`, label: "rows per second" },
              { value: money(s.cost), label: "total cost" },
            ]} />
            {s.errors > 0 && <p className="muted small">{s.errors} rows failed and are left out.</p>}

            <div className="dash">
              <div className="panel">
                <h3>How people feel</h3>
                <BarList items={Object.entries(s.sentiment).map(([k, v]) => ({ label: k, value: v / s.rows, text: `${v} (${pct(v / s.rows)})` }))} />
                <p className="muted small">
                  Jev's sentiment matches the star rating on {pct(s.star_agreement)} of reviews (4-5 stars positive, 3 neutral, 1-2 negative).
                </p>
              </div>
              <div className="panel">
                <h3>Likely to leave</h3>
                <BarList tone="bad" items={Object.entries(s.churn).map(([k, v]) => ({ label: k, value: v / s.rows, text: `${v}` }))} />
              </div>
              <div className="panel wide">
                <h3>Topic by feeling</h3>
                <div className="heat">
                  <span />
                  {["positive", "neutral", "negative"].map((x) => <b key={x}>{x}</b>)}
                  {Object.entries(s.matrix).map(([topic, row]) => (
                    <div className="heat-row" key={topic}>
                      <span className="heat-t">{topic}</span>
                      {["positive", "neutral", "negative"].map((x) => (
                        <span key={x} className={`heat-c ${x}`} style={{ "--a": row[x] / maxMatrix }}>{row[x]}</span>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
              <div className="panel">
                <h3>Share of each topic that reports a bug</h3>
                <BarList tone="amber" items={Object.entries(s.bugs_by_topic).filter(([, v]) => v.all > 0).map(([k, v]) => ({
                  label: k, value: v.bugs / v.all, text: `${v.bugs} of ${v.all}` }))} />
              </div>
              <div className="panel">
                <h3>Reviews to read first</h3>
                <ul className="risky">
                  {s.at_risk.map((r) => (
                    <li key={r.id}><span className="muted small">{r.app.split(".").pop()}, {r.stars} stars</span><span>{r.text}</span></li>
                  ))}
                </ul>
              </div>
            </div>
          </>
        )}
      </section>

      <section id="cost" className="chapter">
        <h2>What it costs</h2>
        {!s && <p className="lede muted">Run the table to see the real cost per row, and where it goes.</p>}
        {s && guide && (
          <>
            <p className="lede">
              This run cost <b>{money(s.cost)}</b> for {s.rows.toLocaleString()} rows: <b>${s.cost_per_row.toFixed(6)}</b> a row.
            </p>
            <div className="panel">
              <h3>Where each row's tokens go</h3>
              <div className="split">
                <span className="q" style={{ flexGrow: questionTokens }} title="the questions" />
                <span className="r" style={{ flexGrow: Math.max(1, s.avg_review_tokens) }} title="the review" />
              </div>
              <p className="muted">
                About <b>{s.avg_tokens}</b> input tokens a row. The review itself is roughly <b>{s.avg_review_tokens}</b> of them. The other{" "}
                <b>{pct(questionTokens / s.avg_tokens)}</b> are the four question definitions, sent again with every row.
              </p>
            </div>

            <div className="panel table-wrap">
              <table>
                <thead><tr><th>Rows</th><th>Cost at this run's price</th><th>Time at this run's speed</th></tr></thead>
                <tbody>
                  {SCALES.map((n) => (
                    <tr key={n}><td>{n.toLocaleString()}</td><td>{money(n * s.cost_per_row)}</td><td>{duration(n / s.rows_per_second)}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="muted">
              {guide.claim.text} At this run's price, {guide.claim.rows.toLocaleString()} rows would be about{" "}
              <b>{money(guide.claim.rows * s.cost_per_row)}</b>, roughly {Math.round((guide.claim.rows * s.cost_per_row) / guide.claim.cost)} times that.
              We cannot tell what their example assumed. Our rows carry four long question definitions each, which is most of the bill, so
              shorter questions or fewer of them would bring the number down. The time column assumes the same 16 calls in flight.
            </p>
          </>
        )}
      </section>

      <section id="how" className="chapter">
        <h2>How it works</h2>
        <p className="lede">Two steps. Jev does the first one; ordinary code does the second.</p>
        {guide && (
          <>
            <ul className="points">
              <li><b>Map:</b> the same four questions are asked about every row, 16 at a time. Each answer is independent of the others.</li>
              <li><b>Reduce:</b> plain code counts the answers, groups them, and ranks them. Nothing is sent to a model.</li>
            </ul>
            <div className="qlist">
              {guide.questions.map((q) => <div key={q.key}><span className="q-kind">{q.kind}</span><span>{q.text}</span></div>)}
            </div>
            <pre>{guide.code}</pre>
          </>
        )}
      </section>
    </>
  );
}
