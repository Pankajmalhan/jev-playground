import { useEffect, useState } from "react";
import { api } from "../api.js";
import Bars from "../components/Bars.jsx";
import ChapterNav from "../components/ChapterNav.jsx";
import ConfidenceLab from "../components/ConfidenceLab.jsx";
import Contrast from "../components/Contrast.jsx";
import Pipeline from "../components/Pipeline.jsx";
import QuestionExplorer from "../components/QuestionExplorer.jsx";
import SpeedPrice from "../components/SpeedPrice.jsx";

const CHAPTERS = [
  { id: "try", label: "Try it" },
  { id: "follow", label: "Follow the message" },
  { id: "questions", label: "The questions" },
  { id: "confidence", label: "Confidence" },
  { id: "compare", label: "Versus a language model" },
  { id: "cost", label: "Speed and price" },
  { id: "fit", label: "Where it fits" },
];

const TYPE_NAME = { noul: "Yes or no", choice: "Pick one", score: "Score" };

export default function WhatIsJev({ usecase }) {
  const [text, setText] = useState("");
  const [picked, setPicked] = useState("");
  const [guide, setGuide] = useState(null);
  const [examples, setExamples] = useState([]);
  const [result, setResult] = useState(null);
  const [roundTrip, setRoundTrip] = useState(null);
  const [history, setHistory] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const loadHistory = () => api.whatIsJev.history().then((d) => setHistory(d.runs)).catch(() => {});

  useEffect(() => {
    api.whatIsJev.guide().then(setGuide).catch(() => {});
    api.whatIsJev.examples().then((d) => setExamples(d.examples)).catch(() => {});
    loadHistory();
  }, []);

  function pick(id) {
    setPicked(id);
    const ex = examples.find((e) => e.id === id);
    if (ex) setText(ex.text);
  }

  async function run() {
    setBusy(true);
    setError("");
    const started = performance.now();
    try {
      const r = await api.whatIsJev.analyze(text);
      setRoundTrip(performance.now() - started);
      setResult(r);
      loadHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  const about = guide?.about;
  const demo = guide?.demo;
  const routing = result?.routing;

  return (
    <>
      <header className="page-head">
        <h1>{usecase.title}</h1>
        {about && (
          <>
            <p className="lead">{about.intro}</p>
            <p className="def">{about.definition}</p>
            <div className="facts">
              {about.facts.map((f) => (
                <div key={f.head}><b>{f.head}</b><span>{f.body}</span></div>
              ))}
            </div>
          </>
        )}
      </header>

      <ChapterNav chapters={CHAPTERS} />

      {/* 1. do something first */}
      <section id="try" className="chapter">
        <h2>Try it</h2>
        <p className="lede">Pick an example or write your own message. Jev answers {demo?.questions.length ?? 5} questions about it in one call.</p>
        <div className="panel">
          <label className="field-label" htmlFor="example">Start from an example</label>
          <select id="example" value={picked} onChange={(e) => pick(e.target.value)}>
            <option value="">Write my own message</option>
            {examples.map((e) => (
              <option key={e.id} value={e.id}>{e.title}</option>
            ))}
          </select>

          <label className="field-label" htmlFor="message">Message</label>
          <textarea
            id="message"
            rows={4}
            value={text}
            onChange={(e) => { setText(e.target.value); setPicked(""); }}
            placeholder="Type or paste a customer message..."
          />
          <button className="primary" disabled={busy || !text.trim()} onClick={run}>
            {busy ? "Asking Jev..." : "Analyze message"}
          </button>
          {error && <div className="error-text">{error}</div>}
        </div>

        {result && (
          <>
            <div className="stats">
              <div><b>{result.seconds.toFixed(2)}s</b><span>time for the one call</span></div>
              <div><b>{result.input_tokens}</b><span>input tokens</span></div>
              <div><b>${result.cost.toFixed(6)}</b><span>cost</span></div>
              <div><b>{result.answers.length}</b><span>answers from that call</span></div>
            </div>

            <div className="answers">
              {result.answers.map((a) => (
                <div className="panel answer" key={a.key}>
                  <div className="answer-type">{TYPE_NAME[a.type] || a.type}</div>
                  <h3>{a.question}</h3>
                  <div className="answer-value">{a.value}</div>
                  <div className="muted small">{(a.confidence * 100).toFixed(0)}% confident</div>
                  <Bars options={a.options} winner={a.value} />
                </div>
              ))}
            </div>

            {routing && (
              <div className={`panel routing${routing.triage ? " triage" : ""}`}>
                <h3>What the app does with these answers</h3>
                <p className="muted small">Plain code, no model: it only reads the numbers above.</p>
                <dl>
                  <div><dt>Send to</dt><dd>{routing.queue}</dd></div>
                  <div><dt>Priority</dt><dd>{routing.priority}: {routing.target}</dd></div>
                </dl>
                <ul>{routing.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
              </div>
            )}
            <p className="next"><a href="#follow">See how that message travelled through the backend</a></p>
          </>
        )}
      </section>

      {/* 2. the backend, interactive */}
      <section id="follow" className="chapter">
        <h2>Follow the message</h2>
        <p className="lede">{demo?.summary}</p>
        {demo && <Pipeline steps={demo.steps} trace={result?.trace} roundTrip={roundTrip} />}
      </section>

      <section id="questions" className="chapter">
        <h2>The questions Jev is asked</h2>
        <p className="lede">
          There are three kinds of question, and this page uses all of them. Each tab shows the question, the code that asks it,
          and what Jev answered on your last run.
        </p>
        {demo && <QuestionExplorer questions={demo.questions} result={result} />}
      </section>

      <section id="confidence" className="chapter">
        <h2>Why a probability beats a label</h2>
        {about && <ConfidenceLab calibration={about.calibration} />}
      </section>

      <section id="compare" className="chapter">
        <h2>Jev versus a language model</h2>
        <p className="lede">The difference is easiest to see in what your code receives. Switch between the two.</p>
        {about && (
          <>
            <Contrast contrast={about.contrast} />
            <details className="more">
              <summary>More differences, side by side</summary>
              <div className="panel table-wrap">
                <table className="compare">
                  <thead><tr>{about.compare.headers.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
                  <tbody>
                    {about.compare.rows.map((r, i) => (
                      <tr key={i}>{r.map((c, j) => (j === 0 ? <th scope="row" key={j}>{c}</th> : <td key={j}>{c}</td>))}</tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </details>
          </>
        )}
      </section>

      <section id="cost" className="chapter">
        <h2>Speed and price</h2>
        <p className="lede">TypeSafe's published figures, with your own measurements next to them.</p>
        {about && <SpeedPrice speed={about.speed} result={result} />}
      </section>

      <section id="fit" className="chapter">
        <h2>Where it fits</h2>
        {about && (
          <>
            <div className="fit">
              <div>
                <h4>Use Jev for</h4>
                <ul>{about.use.map((u) => <li key={u.name}><b>{u.name}</b> <span>{u.note}</span></li>)}</ul>
              </div>
              <div>
                <h4>Use a language model for</h4>
                <ul>{about.avoid.map((u) => <li key={u.name}><b>{u.name}</b> <span>{u.note}</span></li>)}</ul>
              </div>
            </div>
            <details className="more">
              <summary>Why it is called a System One model, and where the name Jev comes from</summary>
              {about.name.map((p, i) => <p key={i} className="muted">{p}</p>)}
            </details>
            <p className="source">
              Source: <a href={about.source.url} target="_blank" rel="noreferrer">{about.source.label}</a>
            </p>
          </>
        )}
      </section>

      {history.length > 0 && (
        <section className="chapter">
          <h2>Recent runs <span className="muted small">(kept in the in-memory database)</span></h2>
          <div className="panel table-wrap">
            <table>
              <thead>
                <tr><th>When</th><th>Message</th><th>Sent to</th><th>Time</th></tr>
              </thead>
              <tbody>
                {history.map((r) => (
                  <tr key={r.id}>
                    <td className="nowrap">{r.created_at}</td>
                    <td>{r.input.text.slice(0, 80)}{r.input.text.length > 80 ? "..." : ""}</td>
                    <td>{r.output.routing ? `${r.output.routing.queue} (${r.output.routing.priority})` : "-"}</td>
                    <td className="nowrap">{r.seconds.toFixed(2)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  );
}
