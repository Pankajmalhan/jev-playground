import Bars from "./Bars.jsx";

const NAMES = { billing: "Billing agent", shipping: "Shipping agent", technical: "Technical agent", finalize: "Verify and reply", human_review: "A person" };
const pct = (p) => `${Math.round(p * 100)}%`;
const ms = (n) => (n >= 1000 ? `${(n / 1000).toFixed(1)} s` : `${Math.round(n)} ms`);

function Meta({ children }) {
  return <span className="tl-meta">{children}</span>;
}

function Supervisor({ e }) {
  const next = e.jev.answers.next_agent;
  const person = e.jev.answers.needs_person;
  const d = e.decision;
  return (
    <article className="tcard jev">
      <header>
        <h3>Round {e.round}: the supervisor</h3>
        <Meta>Jev, {ms(e.ms)}, {e.usage.input_tokens} tokens</Meta>
      </header>

      <div className="tl-cols">
        <div>
          <div className="code-label">Jev was given</div>
          <p className="tl-msg">{e.jev.state_sent.message}</p>
          <p className="muted small">
            {e.jev.state_sent.already_handled.length === 0
              ? "Nothing handled yet."
              : `Already handled: ${e.jev.state_sent.already_handled.map((h) => NAMES[h.agent]).join(", ")}, with their replies.`}
          </p>
          <details className="opt"><summary>the exact input</summary><pre>{JSON.stringify(e.jev.state_sent, null, 2)}</pre></details>
        </div>
        <div>
          <div className="code-label">Who acts next? Jev's probabilities</div>
          <Bars options={Object.fromEntries(Object.entries(next.probabilities).sort((a, b) => b[1] - a[1]))} winner={next.choice} />
          {person !== undefined && (
            <p className="small tl-person">Should a person handle this? <b>{pct(person.noul)}</b> yes</p>
          )}
        </div>
      </div>

      <div className={`tl-decision${d.goto === "human_review" ? " ask" : ""}`}>
        <span className="code-label">Plain code decided</span>
        <b>{d.goto === "human_review" ? "Ask a person" : d.goto === "finalize" ? "Finish: verify and reply" : `Send to the ${NAMES[d.goto]}`}</b>
        <span className="muted">{d.reason}</span>
      </div>
    </article>
  );
}

function Agent({ e }) {
  return (
    <article className="tcard agent">
      <header>
        <h3>{e.title}</h3>
        <Meta>{e.usage.model_calls} model {e.usage.model_calls === 1 ? "call" : "calls"}, {ms(e.ms)}</Meta>
      </header>
      {e.steps.length === 0 ? (
        <p className="muted small">It did not use its tool.</p>
      ) : (
        <ol className="did">
          {e.steps.map((s, i) => (
            <li key={i} className="tool">
              <span className="did-kind">Tool</span>
              <span className="did-note">{s.tool}({Object.values(s.args).join(", ")})</span>
              <span className="did-ms">{s.ms >= 1 ? `${Math.round(s.ms)} ms` : "under 1 ms"}</span>
              <code className="did-result">{JSON.stringify(s.result)}</code>
            </li>
          ))}
        </ol>
      )}
      {e.actions.map((a, i) => (
        <div className="action" key={i}>Action taken: refunded ${a.result.refunded.toFixed(2)} on order #{a.result.order_id}</div>
      ))}
      <blockquote className="reason">{e.reply}</blockquote>
    </article>
  );
}

function Paused({ p, active, onChoose, busy }) {
  return (
    <article className={`tcard pause${active ? "" : " done"}`}>
      <header><h3>{active ? "The workflow is paused" : "The workflow paused here"}</h3><Meta>{active ? "waiting for you" : "answered"}</Meta></header>
      <p>{p.detail}</p>
      <p className="muted small">Jev's best guess was <b>{p.jev_pick}</b> at {pct(p.jev_confidence)}.{active && " You decide where this goes."}</p>
      {active && (
        <div className="choices">
          {p.options.map((o) => (
            <button key={o} className={o === "close" ? "ghost" : "primary"} disabled={busy} onClick={() => onChoose(o)}>
              {o === "close" ? "Finish here" : `Send to ${NAMES[o]?.toLowerCase() ?? o}`}
            </button>
          ))}
        </div>
      )}
    </article>
  );
}

function Finalize({ e }) {
  const v = e.verify;
  return (
    <article className={`tcard jev${e.flagged ? " flag" : ""}`}>
      <header>
        <h3>Verify and reply</h3>
        <Meta>{v ? `Jev, ${ms(e.ms)}, ${e.usage.input_tokens} tokens` : "no reply to check"}</Meta>
      </header>
      {v && (
        <div className="tl-decision">
          <span className="code-label">Jev was asked: does the reply address everything?</span>
          <b>{pct(v.probability)} yes</b>
          <span className="muted">
            {e.flagged ? `Under ${pct(v.threshold)}, so the reply is flagged for a person to check.` : `At or above ${pct(v.threshold)}, so the reply goes out.`}
          </span>
        </div>
      )}
      <div className="code-label">The reply</div>
      <blockquote className="reason final">{e.final}</blockquote>
    </article>
  );
}

export default function RunTimeline({ events, paused, onChoose, busy }) {
  return (
    <div className="tl">
      {events.map((e, i) => {
        if (e.type === "node") {
          if (e.node === "supervisor") return <Supervisor key={i} e={e} />;
          if (e.node === "human_review") return <article key={i} className="tcard human"><h3>A person chose: {e.choice === "close" ? "finish here, with what has been done so far" : NAMES[e.choice]}</h3></article>;
          if (e.node === "finalize") return <Finalize key={i} e={e} />;
          return <Agent key={i} e={e} />;
        }
        if (e.type === "paused") return <Paused key={i} p={e} active={paused === e} onChoose={onChoose} busy={busy} />;
        if (e.type === "done") {
          return (
            <div key={i} className="stats">
              <div><b>{e.seconds.toFixed(1)}s</b><span>whole run</span></div>
              <div><b>{e.jev_calls}</b><span>Jev calls</span></div>
              <div><b>{e.model_calls}</b><span>gpt-4o-mini calls</span></div>
              <div><b>${e.cost.toFixed(5)}</b><span>total cost</span></div>
            </div>
          );
        }
        if (e.type === "error") return <div key={i} className="panel error">{e.message}</div>;
        return null;
      })}
    </div>
  );
}
