import { useEffect, useState } from "react";
import { api } from "../api.js";
import Callout from "../components/Callout.jsx";
import ChapterNav from "../components/ChapterNav.jsx";
import PageHead from "../components/PageHead.jsx";

const CHAPTERS = [
  { id: "try", label: "Try it" },
  { id: "repeat", label: "Run it many times" },
  { id: "how", label: "How the guard works" },
];
const LANES = ["naive", "guarded"];
const money = (v) => `$${Number(v).toFixed(2)}`;
const pct = (p) => `${Math.round(p * 100)}%`;
const LANE_NAME = { naive: "No guard", guarded: "With Jev guard" };

function grade(refunded, owed) {
  if (Math.abs(refunded - owed) < 0.01) return "correct";
  return refunded > owed ? "overpaid" : "short";
}
const GRADE_TEXT = (g, lane) =>
  g === "correct" ? "Correct" : g === "overpaid" ? "Overpaid" : lane === "guarded" ? "Held for a person" : "Under-refunded";

function Verdict({ s }) {
  const j = s.jev;
  return (
    <div className={`gcard ${s.verdict}`}>
      <div className="gc-head"><b>Guard: {s.verdict}</b><span className="muted small">refund {money(s.args.amount)} on order #{s.args.order_id}</span></div>
      <p className="small">{s.why}</p>
      <div className="gc-grid">
        <div><span>charged more than once</span><b>{pct(j.charged_more_than_once)}</b></div>
        <div><span>amount is the extra charge</span><b>{pct(j.amount_is_extra_charge)}</b></div>
        <div><span>message steers the agent</span><b className={j.injection >= 0.5 ? "bad" : ""}>{pct(j.injection)}</b></div>
        <div><span>risk, 0 to 3</span><b>{j.risk}</b></div>
      </div>
      <p className="muted small">
        Hard rule in code: {s.hard_rule.on ? (s.hard_rule.breach ? <b className="bad">breached</b> : "passed") : "turned off for this run"}.
      </p>
    </div>
  );
}

function Lane({ lane, state, scenario }) {
  const r = state.result;
  const g = r && scenario ? grade(r.refunded_total, scenario.expected_refund) : null;
  return (
    <article className={`glane ${lane}`}>
      <header><h3>{LANE_NAME[lane]}</h3>{lane === "guarded" && <span className="lane-role">Jev checks every refund</span>}</header>
      {state.status === "idle" && <p className="muted">{lane === "naive" ? "The agent acts on its own judgement." : "Every refund the agent proposes is checked before it runs."}</p>}
      {state.status === "running" && <p className="muted"><i className="pulse" /> working...</p>}
      {state.status === "error" && <div className="error-text">{state.error}</div>}
      {r && (
        <>
          <div className="gl-total">
            <span className="muted small">Money refunded</span>
            <b>{money(r.refunded_total)}</b>
            {g && <span className={`outcome ${g}`}>{GRADE_TEXT(g, lane)}{scenario && ` (owed ${money(scenario.expected_refund)})`}</span>}
          </div>
          <ol className="did">
            {r.steps.map((s, i) => {
              if (s.type === "guard") return <li key={i} className="guard"><Verdict s={s} /></li>;
              if (s.type === "model") return <li key={i} className="model"><span className="did-kind">Model</span><span className="did-note">{s.note}</span><span className="did-ms">{s.ms} ms</span></li>;
              return (
                <li key={i} className={s.type}>
                  <span className="did-kind">{s.type === "blocked" ? "Stopped" : "Tool"}</span>
                  <span className="did-note">{s.name}({Object.values(s.args).join(", ")})</span>
                  <code className="did-result">{JSON.stringify(s.result)}</code>
                </li>
              );
            })}
          </ol>
          <blockquote className="reason">{r.reply}</blockquote>
          <p className="muted small">{r.seconds}s, {r.model_calls} model calls{r.jev_calls ? `, ${r.jev_calls} Jev ${r.jev_calls === 1 ? "call" : "calls"}` : ""}, ${r.cost.toFixed(5)}</p>
        </>
      )}
    </article>
  );
}

export default function GuardTheAgent({ usecase }) {
  const [guide, setGuide] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [picked, setPicked] = useState("");
  const [text, setText] = useState("");
  const [hardRule, setHardRule] = useState(true);
  const [lanes, setLanes] = useState({ naive: { status: "idle" }, guarded: { status: "idle" } });
  const [stress, setStress] = useState({ status: "idle" });
  const [runs, setRuns] = useState(3);

  useEffect(() => {
    api.guard.guide().then(setGuide).catch(() => {});
    api.guard.scenarios().then((d) => setScenarios(d.scenarios)).catch(() => {});
  }, []);

  const scenario = scenarios.find((s) => s.id === picked);
  const running = LANES.some((l) => lanes[l].status === "running");

  function pick(id) {
    setPicked(id);
    const sc = scenarios.find((s) => s.id === id);
    if (sc) setText(sc.text);
  }

  function run() {
    setLanes({ naive: { status: "running" }, guarded: { status: "running" } });
    LANES.forEach((lane) =>
      api.guard.run(lane, text, hardRule)
        .then((result) => setLanes((p) => ({ ...p, [lane]: { status: "done", result } })))
        .catch((e) => setLanes((p) => ({ ...p, [lane]: { status: "error", error: e.message } })))
    );
  }

  async function runRepeat() {
    setStress({ status: "running", done: 0, total: scenarios.length * 2 * runs });
    try {
      await api.guard.stress(runs, hardRule, (e) => {
        if (e.type === "start") setStress({ status: "running", done: 0, total: e.total });
        if (e.type === "progress") setStress((p) => ({ ...p, done: e.done }));
        if (e.type === "done") setStress({ status: "done", tally: e.tally, runs: e.runs, seconds: e.seconds });
        if (e.type === "error") setStress({ status: "error", error: e.message });
      });
    } catch (err) {
      setStress({ status: "error", error: err.message });
    }
  }

  return (
    <>
      {guide && <PageHead title={usecase.title} lead={guide.intro} roles={guide.roles} />}
      <ChapterNav chapters={CHAPTERS} />

      <section id="try" className="chapter">
        <h2>Try it</h2>
        <p className="lede">Pick a message, or write your own. Both agents get it at the same moment. Order numbers you can use: 1042, 1055, 1060, 1071.</p>
        <div className="panel">
          <label className="field-label" htmlFor="sc">Start from an example</label>
          <select id="sc" value={picked} onChange={(e) => pick(e.target.value)}>
            <option value="">Write my own message</option>
            {scenarios.map((s) => <option key={s.id} value={s.id}>{s.title}</option>)}
          </select>
          <label className="field-label" htmlFor="msg">Customer message</label>
          <textarea id="msg" rows={3} value={text} onChange={(e) => { setText(e.target.value); setPicked(""); }} placeholder="Type a message to the refund agent..." />
          <label className="check">
            <input type="checkbox" checked={hardRule} onChange={(e) => setHardRule(e.target.checked)} />
            <span><b>Keep the hard rule in code</b><span className="muted small">Never refund more than the order amount. Turn it off to see what Jev catches on its own.</span></span>
          </label>
          <button className="primary" disabled={running || !text.trim()} onClick={run}>{running ? "Running both..." : "Run both agents"}</button>
        </div>
        <div className="glanes">
          {LANES.map((l) => <Lane key={l} lane={l} state={lanes[l]} scenario={scenario} />)}
        </div>
        {scenario && lanes.naive.result && lanes.guarded.result && <p className="muted"><b>About this example:</b> {scenario.note}</p>}
        {guide && <Callout title={guide.read_first.title} body={guide.read_first.body} />}
      </section>

      <section id="repeat" className="chapter">
        <h2>Run it many times</h2>
        <p className="lede">One run proves little. This runs every example several times through both agents and counts how each one ended up.</p>
        <div className="panel">
          <div className="code-label">Runs of each example</div>
          <div className="toggle" role="group">
            {[1, 3, 5].map((n) => <button key={n} className={runs === n ? "on" : ""} disabled={stress.status === "running"} onClick={() => setRuns(n)}>{n}</button>)}
          </div>
          <p className="muted small">{scenarios.length * 2 * runs} agent runs in all, a fraction of a cent. It takes about {runs * 8} seconds.</p>
          <button className="primary" disabled={stress.status === "running" || scenarios.length === 0} onClick={runRepeat}>
            {stress.status === "running" ? `Running ${stress.done} of ${stress.total}...` : "Run the repeat test"}
          </button>
          {stress.status === "error" && <div className="error-text">{stress.error}</div>}
        </div>

        {stress.status === "done" && (
          <div className="panel table-wrap">
            <table className="tally">
              <thead>
                <tr><th>Example</th><th>Owed</th><th>No guard</th><th>With Jev guard</th></tr>
              </thead>
              <tbody>
                {scenarios.map((sc) => (
                  <tr key={sc.id}>
                    <td>{sc.title}</td>
                    <td>{money(sc.expected_refund)}</td>
                    {LANES.map((l) => {
                      const t = stress.tally[sc.id][l];
                      return (
                        <td key={l}>
                          <span className="chip-ok">{t.correct} correct</span>
                          {t.overpaid > 0 && <span className="chip-bad">{t.overpaid} overpaid</span>}
                          {t.short > 0 && <span className="chip-hold">{t.short} {l === "guarded" ? "held" : "under-refunded"}</span>}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="muted small tally-note">
              Out of {stress.runs} runs each, in {stress.seconds} s. "Held" means the guard stopped the refund for a person to review, so nothing wrong left the account.
            </p>
          </div>
        )}
      </section>

      <section id="how" className="chapter">
        <h2>How the guard works</h2>
        {guide && (
          <>
            <p className="lede">Before any refund runs, Jev is shown the policy, the customer's message, the order on file and the proposed refund. It answers four questions.</p>
            <div className="qlist">
              {guide.questions.map((q) => <div key={q.key}><span className="q-kind">{q.kind}</span><span>{q.text}</span></div>)}
            </div>
            <div className="verdicts">
              {guide.verdicts.map((v) => <div key={v.name} className={`vd ${v.name.toLowerCase()}`}><b>{v.name}</b><span>{v.line}</span></div>)}
            </div>
            <p className="muted">{guide.why_split}</p>
            <details className="more"><summary>The policy Jev is shown</summary><pre className="prose">{guide.policy}</pre></details>
            <pre>{guide.code}</pre>
          </>
        )}
      </section>
    </>
  );
}
