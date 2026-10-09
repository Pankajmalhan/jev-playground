import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";
import ChapterNav from "../components/ChapterNav.jsx";
import LaneCard from "../components/LaneCard.jsx";
import Picker from "../components/Picker.jsx";

const CHAPTERS = [
  { id: "try", label: "Try it" },
  { id: "compare", label: "Side by side" },
  { id: "pick", label: "Which to use" },
  { id: "built", label: "How each is built" },
];
const LANES = ["jev", "llm", "agent"];
const IDLE = { status: "idle" };

export default function JevVsLlmVsAgents({ usecase }) {
  const [guide, setGuide] = useState(null);
  const [examples, setExamples] = useState([]);
  const [orders, setOrders] = useState([]);
  const [picked, setPicked] = useState("");
  const [text, setText] = useState("");
  const [withOrder, setWithOrder] = useState(false);
  const [lanes, setLanes] = useState({ jev: IDLE, llm: IDLE, agent: IDLE });
  const [now, setNow] = useState(0);
  const [code, setCode] = useState("jev");
  const started = useRef(0);

  useEffect(() => {
    api.jevVsLlm.guide().then(setGuide).catch(() => {});
    api.jevVsLlm.examples().then((d) => setExamples(d.examples)).catch(() => {});
    api.jevVsLlm.orders().then((d) => setOrders(d.orders)).catch(() => {});
  }, []);

  const running = LANES.some((l) => lanes[l].status === "running");
  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setNow(performance.now()), 100);
    return () => clearInterval(t);
  }, [running]);

  const example = examples.find((e) => e.id === picked);

  function pick(id) {
    setPicked(id);
    const ex = examples.find((e) => e.id === id);
    if (ex) setText(ex.text);
  }

  // Start all three lanes at the same moment; each reports when it finishes.
  function run() {
    started.current = performance.now();
    setNow(started.current);
    setLanes({ jev: { status: "running" }, llm: { status: "running" }, agent: { status: "running" } });
    LANES.forEach((lane) => {
      api.jevVsLlm
        .ask(lane, text, withOrder)
        .then((result) => setLanes((p) => ({ ...p, [lane]: { status: "done", result } })))
        .catch((e) => setLanes((p) => ({ ...p, [lane]: { status: "error", error: e.message } })));
    });
  }

  const allDone = LANES.every((l) => lanes[l].status === "done");
  const results = allDone ? Object.fromEntries(LANES.map((l) => [l, lanes[l].result])) : null;
  const elapsed = Math.max(0, (now - started.current) / 1000);

  // A few sentences on how the three finished, using only what was measured.
  function verdict() {
    const name = { jev: "Jev", llm: "The language model", agent: "The agent" };
    const short = { jev: "Jev", llm: "language model", agent: "agent" };
    const best = (f) => LANES.reduce((a, b) => (f(results[a]) <= f(results[b]) ? a : b));
    const fast = best((r) => r.seconds);
    const cheap = best((r) => r.cost);
    const parts = [
      `${name[fast]} was fastest (${results[fast].seconds.toFixed(2)} s).`,
      `${name[cheap]} was cheapest ($${results[cheap].cost.toFixed(5)}).`,
    ];
    const want = example?.expected;
    if (want) {
      const right = (l) => results[l].answers.filter((a) => want[a.key] === a.value).length;
      const total = Object.keys(want).length;
      parts.push(`Against the answer key: ${LANES.map((l) => `${short[l]} ${right(l)}/${total}`).join(", ")}.`);
    }
    return parts.join(" ");
  }

  // Jev's least certain answer: a low number there is a reason to check.
  function unsure() {
    const weakest = results.jev.answers.reduce((a, b) => (a.confidence <= b.confidence ? a : b));
    return weakest.confidence < 0.7 ? weakest : null;
  }

  return (
    <>
      <header className="page-head">
        <h1>{usecase.title}</h1>
        {guide && (
          <>
            <p className="lead">{guide.intro}</p>
            <div className="roles">
              {guide.roles.map((r) => (
                <div key={r.id} className={`role ${r.id}`}>
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
          All three answer the same three questions: which team, how urgent, and is a refund owed. Pick an example and press the button.
          Watch which one finishes first, and which one checks the orders.
        </p>

        <div className="panel">
          <label className="field-label" htmlFor="example">Start from an example</label>
          <select id="example" value={picked} onChange={(e) => pick(e.target.value)}>
            <option value="">Write my own message</option>
            {examples.map((e) => <option key={e.id} value={e.id}>{e.title}</option>)}
          </select>

          <label className="field-label" htmlFor="message">Message</label>
          <textarea
            id="message" rows={3} value={text}
            onChange={(e) => { setText(e.target.value); setPicked(""); }}
            placeholder="Type a customer message. Mention an order such as #1042 to give the agent something to look up."
          />

          {guide && (
            <label className="check">
              <input type="checkbox" checked={withOrder} onChange={(e) => setWithOrder(e.target.checked)} />
              <span>
                <b>{guide.toggle.label}</b>
                <span className="muted small">{guide.toggle.help}</span>
              </span>
            </label>
          )}

          <button className="primary" disabled={running || !text.trim()} onClick={run}>
            {running ? "Running all three..." : "Ask all three"}
          </button>

          <details className="more">
            <summary>The orders table the agent can check</summary>
            <div className="table-wrap orders">
              <table>
                <thead><tr><th>Order</th><th>Customer</th><th>Item</th><th>Amount</th><th>Times charged</th><th>Status</th></tr></thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o.order_id}>
                      <td>#{o.order_id}</td><td>{o.customer}</td><td>{o.item}</td><td>${o.amount.toFixed(2)}</td>
                      <td>{o.times_charged}</td><td>{o.status}, {o.days_since_order} days ago</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </div>

        <div className="lanes">
          {guide && LANES.map((id) => (
            <LaneCard key={id} role={guide.roles.find((r) => r.id === id)} lane={lanes[id]} elapsed={elapsed} expected={example?.expected} />
          ))}
        </div>

        {results && <p className="verdict">{verdict()}</p>}
        {results && unsure() && (
          <p className="verdict gate">
            Jev was only {(unsure().confidence * 100).toFixed(0)}% sure about "{unsure().question.replace(/\?$/, "")}". A low number like that is a
            signal your code can use: when Jev is unsure, hand that message to an agent or a person, and let the confident ones through.
          </p>
        )}
        {results && example?.note && <p className="muted"><b>About this example:</b> {example.note}</p>}

        {guide && (
          <div className="callout">
            <h3>{guide.read_first.title}</h3>
            {guide.read_first.body.map((p, i) => <p key={i}>{p}</p>)}
          </div>
        )}
      </section>

      <section id="compare" className="chapter">
        <h2>Side by side</h2>
        <p className="lede">What each one is, in terms that do not change from run to run.</p>
        {guide && (
          <div className="panel table-wrap">
            <table className="compare four">
              <thead><tr>{guide.compare.headers.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
              <tbody>
                {guide.compare.rows.map((r, i) => (
                  <tr key={i}>{r.map((c, j) => (j === 0 ? <th scope="row" key={j}>{c}</th> : <td key={j}>{c}</td>))}</tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section id="pick" className="chapter">
        <h2>Which one should you use?</h2>
        <p className="lede">Three questions about your own job.</p>
        {guide && <Picker picker={guide.picker} />}
      </section>

      <section id="built" className="chapter">
        <h2>How each one is built</h2>
        <p className="lede">The real code behind each lane, trimmed. The agent is the only one with a loop.</p>
        {guide && (
          <>
            <div className="toggle" role="tablist">
              {guide.code.map((c) => (
                <button key={c.id} role="tab" aria-selected={code === c.id} className={code === c.id ? "on" : ""} onClick={() => setCode(c.id)}>
                  {c.title}
                </button>
              ))}
            </div>
            <pre>{guide.code.find((c) => c.id === code).body}</pre>
          </>
        )}
      </section>
    </>
  );
}
