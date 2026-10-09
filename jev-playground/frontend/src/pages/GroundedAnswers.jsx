import { useEffect, useState } from "react";
import { api } from "../api.js";
import Callout from "../components/Callout.jsx";
import ChapterNav from "../components/ChapterNav.jsx";
import PageHead from "../components/PageHead.jsx";

const CHAPTERS = [
  { id: "ask", label: "Ask a question" },
  { id: "all", label: "Ask all eight" },
  { id: "how", label: "How it works" },
  { id: "kb", label: "The help centre" },
];
const LANES = ["plain", "jev"];
const LANE_NAME = { plain: "Plain retrieval", jev: "Gated by Jev" };
const LEVEL = ["unrelated", "same topic", "partly useful", "answers it"];
const pct = (p) => `${Math.round(p * 100)}%`;

function Lane({ lane, state }) {
  const r = state.result;
  return (
    <article className={`glane ${lane === "jev" ? "guarded" : "naive"}`}>
      <header><h3>{LANE_NAME[lane]}</h3>{lane === "jev" && <span className="lane-role">Jev at three points</span>}</header>
      {state.status === "idle" && <p className="muted">{lane === "plain" ? "Takes the top two keyword matches and asks the model." : "Scores five candidates, gates on whether it can be answered, then checks the answer."}</p>}
      {state.status === "running" && <p className="muted"><i className="pulse" /> working...</p>}
      {state.status === "error" && <div className="error-text">{state.error}</div>}
      {r && (
        <>
          <div className="code-label">{lane === "plain" ? "Passages it read" : "Passages Jev scored"}</div>
          <ul className="pass">
            {r.passages.map((p) => (
              <li key={p.id} className={p.kept ? "kept" : "dropped"}>
                <span>{p.title}</span>
                {p.level !== undefined && <span className={`lvl l${p.level}`}>{LEVEL[p.level]}</span>}
                <span className="muted small">{p.kept ? (lane === "jev" ? "kept" : "") : "dropped"}</span>
              </li>
            ))}
            {r.passages.length === 0 && <li className="muted small">Nothing matched any word in the question.</li>}
          </ul>
          {r.gate && (
            <div className={`gate ${r.gate.open ? "open" : "shut"}`}>
              Can the kept passages answer it? <b>{pct(r.gate.answerable)}</b>. {r.gate.open ? "Gate open, so the model is asked." : `Under ${pct(r.gate.threshold)}, so the model is not asked.`}
            </div>
          )}
          {lane === "jev" && !r.gate && r.passages.length > 0 && <div className="gate shut">No passage was useful enough, so the model was not asked.</div>}
          <div className="code-label">The answer</div>
          <blockquote className={`reason${r.refused ? " refused" : ""}`}>{r.answer}</blockquote>
          {r.check && (
            <div className={`chk ${r.check.flagged ? "flag" : "ok"}`}>
              Jev's check: <b>{pct(r.check.supported)}</b> supported by the passages. {r.check.flagged ? "Flagged: part of this answer may not come from the sources." : "Supported."}
            </div>
          )}
          <p className="muted small">{r.seconds}s, {r.calls.model} model {r.calls.model === 1 ? "call" : "calls"}, {r.calls.jev} Jev {r.calls.jev === 1 ? "call" : "calls"}, ${r.cost.toFixed(5)}</p>
        </>
      )}
    </article>
  );
}

function tally(qs, results, lane) {
  let overRefused = 0, answeredNoSource = 0, flagged = 0, correctRefusals = 0, answers = 0, seconds = 0, cost = 0, n = 0;
  qs.forEach((q) => {
    const r = results[q.id]?.[lane];
    if (!r || r.error) return;
    n++; seconds += r.seconds; cost += r.cost;
    if (q.answerable && r.refused) overRefused++;
    if (!q.answerable && r.refused) correctRefusals++;
    if (!q.answerable && !r.refused) answeredNoSource++;
    if (!r.refused) answers++;
    if (r.check?.flagged) flagged++;
  });
  return { overRefused, answeredNoSource, flagged, correctRefusals, answers, avgSeconds: n ? seconds / n : 0, cost, n };
}

export default function GroundedAnswers({ usecase }) {
  const [guide, setGuide] = useState(null);
  const [qs, setQs] = useState([]);
  const [kb, setKb] = useState([]);
  const [picked, setPicked] = useState("");
  const [text, setText] = useState("");
  const [strict, setStrict] = useState(true);
  const [lanes, setLanes] = useState({ plain: { status: "idle" }, jev: { status: "idle" } });
  const [all, setAll] = useState({ status: "idle" });

  useEffect(() => {
    api.grounded.guide().then(setGuide).catch(() => {});
    api.grounded.questions().then((d) => { setQs(d.questions); setKb(d.knowledge_base); }).catch(() => {});
  }, []);

  const question = qs.find((q) => q.id === picked);
  const running = LANES.some((l) => lanes[l].status === "running");

  function pick(id) {
    setPicked(id);
    const q = qs.find((x) => x.id === id);
    if (q) setText(q.text);
  }
  function ask() {
    setLanes({ plain: { status: "running" }, jev: { status: "running" } });
    LANES.forEach((lane) => api.grounded.ask(lane, text, strict)
      .then((result) => setLanes((p) => ({ ...p, [lane]: { status: "done", result } })))
      .catch((e) => setLanes((p) => ({ ...p, [lane]: { status: "error", error: e.message } }))));
  }
  async function runAll() {
    setAll({ status: "running", done: 0, total: qs.length * 2 });
    try {
      await api.grounded.runAll(strict, (e) => {
        if (e.type === "progress") setAll((p) => ({ ...p, done: e.done, total: e.total }));
        if (e.type === "done") setAll({ status: "done", results: e.results, seconds: e.seconds, strict: e.strict });
        if (e.type === "error") setAll({ status: "error", error: e.message });
      });
    } catch (err) { setAll({ status: "error", error: err.message }); }
  }

  const t = all.status === "done" ? Object.fromEntries(LANES.map((l) => [l, tally(qs, all.results, l)])) : null;
  const answerable = qs.filter((q) => q.answerable).length;

  return (
    <>
      {guide && <PageHead title={usecase.title} lead={guide.intro} roles={guide.roles} />}
      <ChapterNav chapters={CHAPTERS} />

      <section id="ask" className="chapter">
        <h2>Ask a question</h2>
        <p className="lede">Pick one of the eight questions, or write your own. Both pipelines read the same help centre.</p>
        <div className="panel">
          <label className="field-label" htmlFor="q">Start from an example</label>
          <select id="q" value={picked} onChange={(e) => pick(e.target.value)}>
            <option value="">Write my own question</option>
            {qs.map((q) => <option key={q.id} value={q.id}>{q.text}</option>)}
          </select>
          <label className="field-label" htmlFor="qt">Question</label>
          <textarea id="qt" rows={2} value={text} onChange={(e) => { setText(e.target.value); setPicked(""); }} placeholder="Ask the help centre something..." />
          <label className="check">
            <input type="checkbox" checked={strict} onChange={(e) => setStrict(e.target.checked)} />
            <span><b>Tell the model to say "I don't know"</b><span className="muted small">When the passages do not contain the answer. Turn it off to see what a first draft of a prompt does.</span></span>
          </label>
          <button className="primary" disabled={running || !text.trim()} onClick={ask}>{running ? "Asking both..." : "Ask both pipelines"}</button>
        </div>
        <div className="glanes">{LANES.map((l) => <Lane key={l} lane={l} state={lanes[l]} />)}</div>
        {question && lanes.plain.result && lanes.jev.result && (
          <p className="muted"><b>{question.answerable ? "The sources answer this." : "The sources do not answer this."}</b> {question.note}</p>
        )}
        {guide && <Callout title={guide.read_first.title} body={guide.read_first.body} />}
      </section>

      <section id="all" className="chapter">
        <h2>Ask all eight</h2>
        <p className="lede">One question proves little. This asks all eight through both pipelines and counts the mistakes of each kind.</p>
        <div className="panel lab-start">
          <button className="primary" disabled={all.status === "running" || !qs.length} onClick={runAll}>
            {all.status === "running" ? `Running ${all.done} of ${all.total}...` : "Ask all eight"}
          </button>
          <span className="muted small">{strict ? "With" : "Without"} the "I don't know" instruction, as set above.</span>
          {all.status === "error" && <div className="error-text">{all.error}</div>}
        </div>

        {t && (
          <>
            <div className="panel table-wrap">
              <table className="tally">
                <thead><tr><th></th><th>Plain retrieval</th><th>Gated by Jev</th></tr></thead>
                <tbody>
                  <tr><th scope="row">Refused a question the sources do answer<div className="muted small">out of {answerable}</div></th>
                    {LANES.map((l) => <td key={l}><b className={t[l].overRefused ? "bad" : ""}>{t[l].overRefused}</b></td>)}</tr>
                  <tr><th scope="row">Said "I don't know" when the sources do not answer<div className="muted small">out of {qs.length - answerable}, the right call</div></th>
                    {LANES.map((l) => <td key={l}><b>{t[l].correctRefusals}</b></td>)}</tr>
                  <tr><th scope="row">Wrote an answer when the sources do not answer<div className="muted small">out of {qs.length - answerable}, read it to see if it is made up</div></th>
                    {LANES.map((l) => <td key={l}><b className={t[l].answeredNoSource ? "bad" : ""}>{t[l].answeredNoSource}</b></td>)}</tr>
                  <tr><th scope="row">Answers Jev flagged as not fully supported</th>
                    {LANES.map((l) => <td key={l}><b>{t[l].flagged}</b></td>)}</tr>
                  <tr><th scope="row">Average time per question</th>
                    {LANES.map((l) => <td key={l}>{t[l].avgSeconds.toFixed(2)} s</td>)}</tr>
                  <tr><th scope="row">Total cost</th>
                    {LANES.map((l) => <td key={l}>${t[l].cost.toFixed(5)}</td>)}</tr>
                </tbody>
              </table>
            </div>
            <div className="panel table-wrap">
              <table className="mod">
                <thead><tr><th>Question</th><th>Sources answer it?</th><th>Plain retrieval</th><th>Gated by Jev</th></tr></thead>
                <tbody>
                  {qs.map((q) => (
                    <tr key={q.id}>
                      <td>{q.text}</td>
                      <td>{q.answerable ? <span className="lbl">yes</span> : <span className="lbl bad">no</span>}</td>
                      {LANES.map((l) => {
                        const r = all.results[q.id]?.[l];
                        if (!r || r.error) return <td key={l} className="bad">error</td>;
                        return (
                          <td key={l}>
                            <details><summary>{r.refused ? "I don't know" : r.answer.slice(0, 70) + (r.answer.length > 70 ? "..." : "")}{r.check?.flagged && <b className="mistake"> (flagged)</b>}</summary>
                              <p className="small muted">{r.answer}</p></details>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="muted small">{all.seconds} s for all {qs.length * 2} runs.</p>
          </>
        )}
      </section>

      <section id="how" className="chapter">
        <h2>How it works</h2>
        {guide && (
          <>
            <p className="lede">Five steps. Jev does three of them, each a different kind of question.</p>
            <ol className="rsteps">
              {guide.steps.map((s) => (
                <li key={s.n} className={s.who === "Jev" ? "jev" : ""}><span className="dn">{s.n}</span><div><b>{s.title}</b> <span className="who">{s.who}</span><p className="muted">{s.line}</p></div></li>
              ))}
            </ol>
            <pre>{guide.code}</pre>
          </>
        )}
      </section>

      <section id="kb" className="chapter">
        <h2>The help centre</h2>
        <p className="lede">The twelve short articles both pipelines search. Read them to judge the answers yourself.</p>
        <div className="kb">
          {kb.map((p) => <details key={p.id}><summary>{p.title}</summary><p>{p.text}</p></details>)}
        </div>
      </section>
    </>
  );
}
