import { useState } from "react";

// Three yes/no questions that point to Jev, a language model, code + Jev, or an agent.
export default function Picker({ picker }) {
  const [a, setA] = useState({ facts: null, known: null, words: null });
  const set = (id, v) => setA((prev) => ({ ...prev, [id]: v }));

  let key = null;
  if (a.facts === false) key = a.words ? "llm" : "jev";
  else if (a.facts === true && a.known !== null) key = a.known ? "code" : "agent";
  const result = key && picker.results[key];
  const addWords = a.words && (key === "code" || key === "agent");

  return (
    <div className="picker">
      {picker.questions
        .filter((q) => !q.only_if || a[q.only_if] === true)
        .map((q) => (
          <div className="pq" key={q.id}>
            <div>
              <div className="pq-text">{q.text}</div>
              <div className="muted small">For example: {q.example}</div>
            </div>
            <div className="yn" role="group" aria-label={q.text}>
              {[["Yes", true], ["No", false]].map(([label, v]) => (
                <button key={label} className={a[q.id] === v ? "on" : ""} aria-pressed={a[q.id] === v} onClick={() => set(q.id, v)}>
                  {label}
                </button>
              ))}
            </div>
          </div>
        ))}

      <div className={`pick-result${result ? " has" : ""}`} aria-live="polite">
        {result ? (
          <>
            <div className="code-label">Use</div>
            <h3>{result.title}</h3>
            <p>{result.why}</p>
            {addWords && <p className="muted">{picker.words_note}</p>}
          </>
        ) : (
          <p className="muted">Answer the questions above and the right tool appears here.</p>
        )}
      </div>
    </div>
  );
}
