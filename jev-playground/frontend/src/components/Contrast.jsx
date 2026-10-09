import { useState } from "react";

// What your code actually receives: a paragraph to parse, or a value to use.
export default function Contrast({ contrast }) {
  const [side, setSide] = useState("llm");
  const c = contrast[side];
  return (
    <div>
      <div className="toggle" role="tablist">
        {["llm", "jev"].map((k) => (
          <button key={k} role="tab" aria-selected={side === k} className={side === k ? "on" : ""} onClick={() => setSide(k)}>
            {contrast[k].label}
          </button>
        ))}
      </div>
      <div className={`contrast ${side}`}>
        <div>
          <div className="code-label">What comes back</div>
          <pre className={side === "llm" ? "prose" : ""}>{c.output}</pre>
        </div>
        <div>
          <div className="code-label">What your code does with it</div>
          <pre>{c.code}</pre>
        </div>
      </div>
      <ul className="points">
        {c.points.map((p, i) => <li key={i}>{p}</li>)}
      </ul>
      <p className="muted small">{contrast.note}</p>
    </div>
  );
}
