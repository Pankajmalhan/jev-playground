import { useEffect, useState } from "react";
import { api } from "../api.js";
import AgentGraph from "../components/AgentGraph.jsx";
import ChapterNav from "../components/ChapterNav.jsx";
import RunTimeline from "../components/RunTimeline.jsx";

const CHAPTERS = [
  { id: "try", label: "Try it" },
  { id: "decide", label: "How Jev decides" },
  { id: "shapes", label: "Why a supervisor" },
  { id: "built", label: "How it is built" },
];

export default function JevSupervisor({ usecase }) {
  const [guide, setGuide] = useState(null);
  const [examples, setExamples] = useState([]);
  const [orders, setOrders] = useState([]);
  const [picked, setPicked] = useState("");
  const [text, setText] = useState("");
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState("idle"); // idle, running, paused, done, error
  const [paused, setPaused] = useState(null);
  const [code, setCode] = useState("graph");

  const loadOrders = () => api.supervisor.orders().then((d) => setOrders(d.orders)).catch(() => {});

  useEffect(() => {
    api.supervisor.guide().then(setGuide).catch(() => {});
    api.supervisor.examples().then((d) => setExamples(d.examples)).catch(() => {});
    loadOrders();
  }, []);

  const example = examples.find((e) => e.id === picked);

  function pick(id) {
    setPicked(id);
    const ex = examples.find((e) => e.id === id);
    if (ex) setText(ex.text);
  }

  // Each line from the server is one step. Add it to the list and keep the status current.
  function onEvent(e) {
    setEvents((prev) => [...prev, e]);
    if (e.type === "paused") { setPaused(e); setStatus("paused"); }
    if (e.type === "done") { setStatus("done"); loadOrders(); }
    if (e.type === "error") setStatus("error");
  }

  async function start(call) {
    try {
      await call();
    } catch (err) {
      setEvents((prev) => [...prev, { type: "error", message: err.message }]);
      setStatus("error");
    }
  }

  function run() {
    setEvents([]);
    setPaused(null);
    setStatus("running");
    start(() => api.supervisor.run(text, onEvent));
  }

  function choose(choice) {
    const threadId = paused.thread_id;
    setPaused(null);
    setStatus("running");
    start(() => api.supervisor.resume(threadId, choice, onEvent));
  }

  // The nodes visited, in order, for the graph.
  const trail = [];
  events.forEach((e) => {
    const node = e.type === "node" ? e.node : e.type === "paused" ? "human_review" : null;
    if (node && trail[trail.length - 1] !== node) trail.push(node);
  });
  // The moment Jev decides, light up where it sent the message, before that step finishes.
  const lastEvent = events[events.length - 1];
  if (lastEvent?.type === "node" && lastEvent.node === "supervisor" && trail[trail.length - 1] !== lastEvent.decision.goto) {
    trail.push(lastEvent.decision.goto);
  }
  const running = status === "running";
  const waiting = status === "paused";

  return (
    <>
      <header className="page-head">
        <h1>{usecase.title}</h1>
        {guide && (
          <>
            <p className="lead">{guide.intro}</p>
            <div className="roles">
              {guide.cast.map((r) => (
                <div key={r.id} className={`role ${r.id === "jev" ? "jev" : ""}`}>
                  <span className="lane-role">{r.role}</span>
                  <b>{r.name}</b>
                  <span>{r.line}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </header>

      <ChapterNav chapters={CHAPTERS} />

      <section id="try" className="chapter">
        <h2>Try it</h2>
        <p className="lede">
          Pick a message and run the workflow. The graph lights up along the path as each step finishes, and every step is explained below it.
        </p>

        <div className="panel">
          <label className="field-label" htmlFor="example">Start from an example</label>
          <select id="example" value={picked} onChange={(e) => pick(e.target.value)}>
            <option value="">Write my own message</option>
            {examples.map((e) => <option key={e.id} value={e.id}>{e.title}</option>)}
          </select>
          <label className="field-label" htmlFor="message">Customer message</label>
          <textarea
            id="message" rows={3} value={text}
            onChange={(e) => { setText(e.target.value); setPicked(""); }}
            placeholder="Type a message. Mention orders such as #1042, #1055, #1060 or #1071 to give the specialists something to look up."
          />
          <button className="primary" disabled={running || waiting || !text.trim()} onClick={run}>
            {running ? "Running..." : "Run the workflow"}
          </button>

          <details className="more">
            <summary>The orders the specialists can use</summary>
            <div className="table-wrap orders">
              <table>
                <thead><tr><th>Order</th><th>Item</th><th>Amount</th><th>Times charged</th><th>Status</th><th>Refunded</th></tr></thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o.order_id}>
                      <td>#{o.order_id}</td><td>{o.item}</td><td>${o.amount.toFixed(2)}</td><td>{o.times_charged}</td>
                      <td>{o.status}, {o.days_since_order} days ago</td><td>{o.refunded > 0 ? `$${o.refunded.toFixed(2)}` : "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </div>

        <AgentGraph trail={trail} running={running} waiting={waiting} />

        <RunTimeline events={events} paused={paused} onChoose={choose} busy={running} />
        {running && <p className="muted working"><i className="pulse" /> working...</p>}
        {example && status === "done" && <p className="muted"><b>About this example:</b> {example.note}</p>}

        {guide && (
          <div className="callout">
            <h3>{guide.read_first.title}</h3>
            {guide.read_first.body.map((p, i) => <p key={i}>{p}</p>)}
          </div>
        )}
      </section>

      <section id="decide" className="chapter">
        <h2>How Jev decides</h2>
        <p className="lede">Jev is asked four questions during a run. For each one, Jev supplies the numbers and plain code applies a rule to them.</p>
        {guide && (
          <ol className="decisions">
            {guide.decisions.map((d) => (
              <li key={d.n}>
                <span className="dn">{d.n}</span>
                <div>
                  <h3>{d.title}</h3>
                  <p><span className="dk">Jev</span> {d.asks}</p>
                  <p><span className="dk">Rule</span> {d.rule}</p>
                </div>
              </li>
            ))}
          </ol>
        )}
      </section>

      <section id="shapes" className="chapter">
        <h2>Why a supervisor, and which kind</h2>
        {guide && (
          <>
            <p className="lede">{guide.why_jev}</p>
            <div className="panel table-wrap">
              <table className="compare">
                <thead><tr>{guide.shapes.headers.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
                <tbody>
                  {guide.shapes.rows.map((r, i) => (
                    <tr key={i} className={r[0].includes("this build") ? "mine" : ""}>
                      {r.map((c, j) => (j === 0 ? <th scope="row" key={j}>{c}</th> : <td key={j}>{c}</td>))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3 className="sub">Two ways to wire the supervisor</h3>
            <div className="fit">
              {guide.shapes.wiring.map((w) => (
                <div key={w.title}><h4>{w.title}</h4><p className="muted">{w.body}</p></div>
              ))}
            </div>
          </>
        )}
      </section>

      <section id="built" className="chapter">
        <h2>How it is built</h2>
        <p className="lede">The real code, trimmed. LangGraph provides the graph and the pause; Jev and the specialists are ordinary function calls.</p>
        {guide && (
          <>
            <div className="toggle" role="tablist">
              {guide.code.map((c) => (
                <button key={c.id} role="tab" aria-selected={code === c.id} className={code === c.id ? "on" : ""} onClick={() => setCode(c.id)}>{c.title}</button>
              ))}
            </div>
            <pre>{guide.code.find((c) => c.id === code).body}</pre>
          </>
        )}
      </section>
    </>
  );
}
