import { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";
import Callout from "../components/Callout.jsx";
import ChapterNav from "../components/ChapterNav.jsx";
import PageHead from "../components/PageHead.jsx";

const CHAPTERS = [
  { id: "run", label: "Run it" },
  { id: "route", label: "Move the line" },
  { id: "prompts", label: "The prompts" },
  { id: "how", label: "How it works" },
];
const LEVELS = ["Trivial", "Easy", "Moderate", "Hard"];
const money = (v) => (v < 0.001 ? `$${v.toFixed(5)}` : v < 1 ? `$${v.toFixed(4)}` : `$${v.toFixed(2)}`);
const pct = (p) => `${Math.round(p * 100)}%`;
const avg = (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);

function strategy(rows, pickBig) {
  const chosen = rows.map((r) => ({ r, big: pickBig(r) }));
  const part = (c) => (c.big ? c.r.big : c.r.small);
  return {
    cost: chosen.reduce((a, c) => a + part(c).cost, 0),
    time: avg(chosen.map((c) => part(c).seconds)),
    quality: avg(chosen.map((c) => part(c).judge.good)),
    shaky: chosen.filter((c) => part(c).judge.good < 0.6).length,
    bigCount: chosen.filter((c) => c.big).length,
  };
}

export default function ModelRouter({ usecase }) {
  const [guide, setGuide] = useState(null);
  const [rows, setRows] = useState([]);
  const [status, setStatus] = useState("idle");
  const [total, setTotal] = useState(12);
  const [secs, setSecs] = useState(null);
  const [error, setError] = useState("");
  const [line, setLine] = useState(2);

  useEffect(() => { api.router.guide().then(setGuide).catch(() => {}); }, []);

  async function run() {
    setStatus("running"); setRows([]); setError(""); setSecs(null);
    try {
      await api.router.run((e) => {
        if (e.type === "start") setTotal(e.total);
        if (e.type === "prompt") setRows((p) => [...p, e].sort((a, b) => a.id - b.id));
        if (e.type === "done") { setSecs(e.seconds); setStatus("done"); }
        if (e.type === "error") { setError(e.message); setStatus("idle"); }
      });
    } catch (err) { setError(err.message); setStatus("idle"); }
  }

  const done = status === "done";
  const routeMs = avg(rows.map((r) => r.route.ms)) / 1000;
  const routerCost = rows.reduce((a, r) => a + r.route.cost, 0);
  const judgeCost = rows.reduce((a, r) => a + r.small.judge.cost + r.big.judge.cost, 0);

  const s = useMemo(() => {
    if (!rows.length) return null;
    const big = strategy(rows, () => true);
    const small = strategy(rows, () => false);
    const routed = strategy(rows, (r) => r.route.difficulty >= line);
    routed.time += routeMs;
    return { big, small, routed };
  }, [rows, line, routeMs]);

  const cards = s && [
    { key: "big", title: "Always the big model", data: s.big },
    { key: "routed", title: "Routed by Jev", data: s.routed, hot: true },
    { key: "small", title: "Always the small model", data: s.small },
  ];

  return (
    <>
      {guide && <PageHead title={usecase.title} lead={guide.intro} roles={guide.roles} />}
      <ChapterNav chapters={CHAPTERS} />

      <section id="run" className="chapter">
        <h2>Run it</h2>
        <p className="lede">Twelve prompts, from "what is the capital of Australia" to "compare two caching strategies". Each is answered by both models and rated by Jev.</p>
        <div className="panel lab-start">
          <button className="primary" disabled={status === "running"} onClick={run}>{status === "running" ? `Running ${rows.length} of ${total}...` : done ? "Run again" : "Run the 12 prompts"}</button>
          {done && <span className="muted small">{secs} s. Both models answered all {rows.length}.</span>}
          {error && <div className="error-text">{error}</div>}
        </div>
        {guide && <Callout title={guide.read_first.title} body={guide.read_first.body} />}
      </section>

      <section id="route" className="chapter">
        <h2>Move the line</h2>
        {!s && <p className="lede muted">Run the prompts, then decide where the line goes.</p>}
        {s && guide && (
          <>
            <div className="panel">
              <label htmlFor="line" className="thr-label">
                Rule: <b className="amber">{guide.rules[line].label}</b>
              </label>
              <input id="line" type="range" min="0" max="4" value={line} onChange={(e) => setLine(+e.target.value)} />
              <div className="thr-hint muted small"><span>more to the big model</span><span>more to the small model</span></div>
            </div>

            <div className="strats">
              {cards.map((c) => (
                <div key={c.key} className={`strat${c.hot ? " hot" : ""}`}>
                  <h3>{c.title}</h3>
                  <div className="st-cost">{money(c.data.cost)}</div>
                  <div className="muted small">to answer all {rows.length}{c.hot && `, ${c.data.bigCount} of them on the big model`}</div>
                  <dl>
                    <div><dt>Average time</dt><dd>{c.data.time.toFixed(2)} s</dd></div>
                    <div><dt>Quality, by Jev</dt><dd>{pct(c.data.quality)}</dd></div>
                    <div><dt>Shaky answers</dt><dd className={c.data.shaky ? "bad" : ""}>{c.data.shaky}</dd></div>
                  </dl>
                </div>
              ))}
            </div>
            <p className="verdict">
              {line === 0 || line === 4
                ? "At this end nothing is routed, so these two are just the two models on their own."
                : `Routed answers cost ${pct(1 - s.routed.cost / s.big.cost)} less than always using the big model, at ${pct(s.routed.quality)} judged quality against ${pct(s.big.quality)}.`}
            </p>
            <p className="muted">
              Jev's rating of each prompt cost {money(routerCost)} for these {rows.length}, and added about {routeMs.toFixed(2)} s to each, which the routed time already includes.
              {" "}For this demonstration Jev also judged every answer from both models, which cost another {money(judgeCost)} and would not run in real use.
            </p>
          </>
        )}
      </section>

      <section id="prompts" className="chapter">
        <h2>The prompts</h2>
        {!rows.length && <p className="lede muted">The prompts appear here as they finish.</p>}
        {rows.length > 0 && (
          <div className="panel table-wrap">
            <table className="rt">
              <thead><tr><th>Prompt</th><th>Jev's rating</th><th>Goes to</th><th>Small, judged</th><th>Big, judged</th><th>Cost small / big</th></tr></thead>
              <tbody>
                {rows.map((r) => {
                  const big = r.route.difficulty >= line;
                  return (
                    <tr key={r.id}>
                      <td>
                        <details><summary>{r.text}</summary>
                          <div className="ans"><b>Small</b><p>{r.small.text}</p><b>Big</b><p>{r.big.text}</p></div>
                        </details>
                      </td>
                      <td><span className={`lvl l${r.route.difficulty}`}>{LEVELS[r.route.difficulty]}</span><span className="muted small"> {r.route.task}</span></td>
                      <td>{big ? "big" : "small"}</td>
                      <td className={r.small.judge.good < 0.6 ? "bad" : ""}>{pct(r.small.judge.good)}</td>
                      <td className={r.big.judge.good < 0.6 ? "bad" : ""}>{pct(r.big.judge.good)}</td>
                      <td className="nowrap">{money(r.small.cost)} / {money(r.big.cost)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section id="how" className="chapter">
        <h2>How it works</h2>
        {guide && (
          <>
            <p className="lede">Jev rates every prompt on a four-step scale, and a rule you choose turns that rating into a model.</p>
            <ol className="scale4">
              {guide.scale.map((x) => <li key={x.level} className={`l${x.level}`}><b>{x.name}</b><span>{x.line}</span></li>)}
            </ol>
            <pre>{guide.code}</pre>
          </>
        )}
      </section>
    </>
  );
}
