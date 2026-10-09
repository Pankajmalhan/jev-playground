import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";
import BarList from "../components/BarList.jsx";
import Callout from "../components/Callout.jsx";
import ChapterNav from "../components/ChapterNav.jsx";
import PageHead from "../components/PageHead.jsx";
import Stats from "../components/Stats.jsx";

const CHAPTERS = [
  { id: "policy", label: "The policy" },
  { id: "claims", label: "The claims" },
  { id: "own", label: "Try your own" },
  { id: "how", label: "How it works" },
];
const pct = (p) => `${Math.round(p * 100)}%`;
const ACTION = { approve: "Approved automatically", reject: "Rejected automatically", manager: "Sent to a manager" };
const facts = (d) => [d.category, `$${d.amount}`, d.receipt === false ? "no receipt" : d.receipt ? "receipt" : null, d.people ? `${d.people} ${d.people === 1 ? "person" : "people"}` : null,
  d.nights ? `${d.nights} night${d.nights > 1 ? "s" : ""}` : null, d.class ? `${d.class} class` : null, d.alcohol ? "alcohol" : null,
  d.days_since_expense > 30 ? `${d.days_since_expense} days old` : null].filter(Boolean).join(", ");

export default function StructuredDecisions({ usecase }) {
  const [guide, setGuide] = useState(null);
  const [defaults, setDefaults] = useState(null);
  const [policy, setPolicy] = useState("");
  const [calculate, setCalculate] = useState(true);
  const [result, setResult] = useState(null);
  const [previous, setPrevious] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [json, setJson] = useState("");
  const [one, setOne] = useState(null);
  const lastPolicy = useRef("");

  useEffect(() => {
    api.decisions.guide().then(setGuide).catch(() => {});
    api.decisions.examples().then((d) => {
      setDefaults(d);
      setPolicy(d.policy);
      setJson(JSON.stringify(d.expenses[1].data, null, 2));
    }).catch(() => {});
  }, []);

  async function runAll() {
    setBusy(true); setError("");
    try {
      const r = await api.decisions.batch(policy, calculate);
      setPrevious(result && lastPolicy.current !== policy ? result : previous);
      lastPolicy.current = policy;
      setResult(r);
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  async function runOne() {
    setOne(null);
    try { setOne(await api.decisions.decide(JSON.parse(json), policy, calculate)); }
    catch (e) { setOne({ error: e instanceof SyntaxError ? "That is not valid JSON." : e.message }); }
  }

  function experiment(x) {
    if (!policy.includes(x.find)) return;
    setPolicy(policy.replace(x.find, x.replace));
  }

  const rows = result?.rows ?? [];
  const disagree = rows.filter((r) => r.decision !== r.code).length;
  const manager = rows.filter((r) => r.action === "manager").length;
  const matchKey = rows.filter((r) => r.decision === r.expected).length;
  const prevById = previous ? Object.fromEntries(previous.rows.map((r) => [r.id, r])) : {};

  return (
    <>
      {guide && <PageHead title={usecase.title} lead={guide.intro} roles={guide.roles} />}
      <ChapterNav chapters={CHAPTERS} />

      <section id="policy" className="chapter">
        <h2>The policy</h2>
        <p className="lede">This is the whole rule book. Edit it, or press a button to change one rule, then decide the claims again.</p>
        <div className="panel">
          <label className="field-label" htmlFor="pol">Expense policy, in plain English</label>
          <textarea id="pol" className="policy-box" rows={9} value={policy} onChange={(e) => setPolicy(e.target.value)} />
          <div className="chips2">
            {guide?.experiments.map((x) => (
              <button key={x.label} className="ghost" disabled={!policy.includes(x.find)} onClick={() => experiment(x)} title={policy.includes(x.find) ? "" : "That rule has already been changed"}>{x.label}</button>
            ))}
            <button className="ghost" onClick={() => defaults && setPolicy(defaults.policy)}>Reset the policy</button>
          </div>
          <label className="check">
            <input type="checkbox" checked={calculate} onChange={(e) => setCalculate(e.target.checked)} />
            <span><b>Let code do the arithmetic first</b><span className="muted small">Code works out the per-person and per-night amounts and hands them to Jev with the claim.</span></span>
          </label>
          <button className="primary" disabled={busy || !defaults} onClick={runAll}>{busy ? "Deciding..." : result ? "Decide all 8 claims again" : "Decide all 8 claims"}</button>
          {error && <div className="error-text">{error}</div>}
        </div>
        {guide && <Callout title={guide.read_first.title} body={guide.read_first.body} />}
      </section>

      <section id="claims" className="chapter">
        <h2>The claims</h2>
        {!result && <p className="lede muted">Decide the claims above and the results appear here.</p>}
        {result && (
          <>
            <Stats items={[
              { value: `${manager} of ${rows.length}`, label: "sent to a manager" },
              { value: `${rows.length - manager} of ${rows.length}`, label: "decided without a person" },
              { value: result.default_policy ? `${matchKey} of ${rows.length}` : "-", label: result.default_policy ? "match our reading" : "key only for the default policy" },
              { value: `${disagree} of ${rows.length}`, label: "differ from the code rules" },
            ]} />
            <div className="panel table-wrap">
              <table className="dec">
                <thead><tr><th>Claim</th><th>Jev decides</th><th>What happens</th><th>Quick code rules</th>{result.default_policy && <th>Our reading</th>}</tr></thead>
                <tbody>
                  {rows.map((r) => {
                    const before = prevById[r.id];
                    return (
                      <tr key={r.id}>
                        <td><b>{r.title}</b><div className="muted small">{facts(r.data)}</div>
                          <details className="opt"><summary>the exact input</summary><pre>{JSON.stringify(r.state_sent, null, 2)}</pre></details></td>
                        <td>
                          <span className={`dv ${r.decision}`}>{r.decision}</span> <span className="muted small">{pct(r.decision_p)}</span>
                          {before && before.decision !== r.decision && <div className="changed">was {before.decision}</div>}
                          <div className="muted small">complies: {pct(r.within_policy)}</div>
                        </td>
                        <td><span className={`act ${r.action}`}>{ACTION[r.action]}</span><div className="muted small">{r.why}</div></td>
                        <td><span className={`dv ${r.code}`}>{r.code}</span>{r.code !== r.decision && <div className="muted small">differs</div>}</td>
                        {result.default_policy && <td><span className={`dv ${r.expected}`}>{r.expected}</span>{r.decision === r.expected ? <span className="ok"> match</span> : <span className="bad"> differs</span>}</td>}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="muted small">{rows.length} decisions in {result.seconds} s for ${result.cost.toFixed(5)}. The code rules do not read the policy text, so they stay the same when you edit it.</p>
          </>
        )}
      </section>

      <section id="own" className="chapter">
        <h2>Try your own claim</h2>
        <p className="lede">The claim is JSON: change the amount, the category, or add fields of your own. It is judged against the policy above.</p>
        <div className="panel">
          <textarea className="json-box" rows={12} value={json} onChange={(e) => setJson(e.target.value)} spellCheck={false} />
          <button className="primary" disabled={!json.trim()} onClick={runOne}>Decide this claim</button>
          {one?.error && <div className="error-text">{one.error}</div>}
          {one && !one.error && (
            <div className="one">
              <div><span className="code-label">Jev decides</span><b className={`dv ${one.decision}`}>{one.decision}</b>
                <BarList items={Object.entries(one.options).sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ label: k, value: v, text: pct(v) }))} /></div>
              <div><span className="code-label">What happens</span><b>{ACTION[one.action]}</b><p className="muted small">{one.why}</p>
                <p className="muted small">Complies with the policy: {pct(one.within_policy)}. Fraud risk: level {one.fraud} of 3. Quick code rules say: {one.code}.</p></div>
            </div>
          )}
        </div>
      </section>

      <section id="how" className="chapter">
        <h2>How it works</h2>
        {guide && (
          <>
            <p className="lede">Jev is asked three questions about every claim. A short rule in code turns its answers into an action.</p>
            <div className="qlist">
              {guide.questions.map((q) => <div key={q.key}><span className="q-kind">{q.kind}</span><span>{q.text}</span></div>)}
            </div>
            <ul className="points">
              <li>Approve automatically only if Jev says approve and is at least {pct(guide.thresholds.approve)} sure the claim complies.</li>
              <li>Reject automatically only if Jev says reject and puts no more than {pct(guide.thresholds.reject)} on it complying.</li>
              <li>Anything else, or a fraud risk above level {guide.thresholds.fraud}, goes to a manager.</li>
            </ul>
            <pre>{guide.code}</pre>
          </>
        )}
      </section>
    </>
  );
}
