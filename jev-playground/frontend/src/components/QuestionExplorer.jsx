import { useState } from "react";
import Bars from "./Bars.jsx";

// The five questions as tabs: what is asked, the code that asks it, and what
// Jev answered the last time you ran a message.
export default function QuestionExplorer({ questions, result }) {
  const [key, setKey] = useState(questions[0].key);
  const q = questions.find((x) => x.key === key);
  const answer = result?.answers.find((a) => a.key === key);

  return (
    <div className="qx">
      <div className="qtabs" role="tablist">
        {questions.map((x) => (
          <button key={x.key} role="tab" aria-selected={x.key === key} className={`qtab${x.key === key ? " on" : ""}`} onClick={() => setKey(x.key)}>
            <span className="q-kind">{x.kind}</span>
            {x.tab}
          </button>
        ))}
      </div>

      <div className="qpanel">
        <div>
          <h3>{q.question}</h3>
          <p className="muted small">{q.returns}</p>
          <ul className="opts">
            {q.options.map((o) => (
              <li key={o.name}><b>{o.name}</b> <span>{o.meaning}</span></li>
            ))}
          </ul>
          <div className="code-label">How it is written in code</div>
          <pre>{q.code}</pre>
        </div>

        <div className="qlive">
          <div className="code-label">Jev's answer on your last run</div>
          {answer ? (
            <>
              <div className="answer-value">{answer.value}</div>
              <div className="muted small">{(answer.confidence * 100).toFixed(0)}% confident</div>
              <Bars options={answer.options} winner={answer.value} />
            </>
          ) : (
            <p className="muted">Run a message above and Jev's answer to this question appears here.</p>
          )}
        </div>
      </div>
    </div>
  );
}
