import { useState } from "react";

const LO = Math.log10(0.05);
const HI = Math.log10(400);
const pos = (s) => `${((Math.log10(Math.min(Math.max(s, 0.05), 400)) - LO) / (HI - LO)) * 100}%`;
const COUNTS = [1_000, 10_000, 100_000, 1_000_000, 10_000_000];
const TICKS = [[0.1, "0.1 s"], [1, "1 s"], [10, "10 s"], [100, "100 s"]];

function money(v) {
  if (v < 0.01) return "under $0.01";
  if (v < 100) return `$${v.toFixed(2)}`;
  return `$${Math.round(v).toLocaleString()}`;
}

// TypeSafe's published ranges on a log scale, with your own measured call (and,
// if you have one, a language model you timed yourself) placed on it, and the
// input cost of a workload at your real token count.
export default function SpeedPrice({ speed, result }) {
  const [i, setI] = useState(2);
  const [mine, setMine] = useState("");
  const n = COUNTS[i];
  const tokens = result?.input_tokens ?? speed.default_tokens;
  const mtok = (n * tokens) / 1_000_000;
  const jev = mtok * speed.jev_input_per_mtok;
  const [lo, hi] = speed.llm_input_per_mtok;
  const mySeconds = parseFloat(mine);
  const hasMine = mySeconds > 0;
  const slower = result && result.seconds * 1000 > speed.jev_seconds[1] * 1000;

  return (
    <div>
      <div className="callout">
        <h3>{speed.read_first.title}</h3>
        {speed.read_first.body.map((p, k) => <p key={k}>{p}</p>)}
      </div>

      <div className="scale" aria-label="Response time on a log scale">
        {TICKS.map(([v, label]) => (
          <span key={v} className="tick" style={{ left: pos(v) }}><i />{label}</span>
        ))}
        <div className="srow"><span className="slabel">{speed.llm_label}</span>
          <span className="sbar llm" style={{ left: pos(speed.llm_seconds[0]), width: `calc(${pos(speed.llm_seconds[1])} - ${pos(speed.llm_seconds[0])})` }}>3 to 329 s</span>
        </div>
        <div className="srow"><span className="slabel">Jev, TypeSafe's figure</span>
          <span className="sbar jev" style={{ left: pos(speed.jev_seconds[0]), width: `calc(${pos(speed.jev_seconds[1])} - ${pos(speed.jev_seconds[0])})` }} />
          <span className="sval" style={{ left: `calc(${pos(speed.jev_seconds[1])} + 8px)` }}>70 to 500 ms</span>
        </div>
        <div className="srow"><span className="slabel">Jev, your call</span>
          {result ? (
            <>
              <span className="you" style={{ left: pos(result.seconds) }} />
              <span className="sval you-t" style={{ left: `calc(${pos(result.seconds)} + 12px)` }}>{result.seconds.toFixed(2)} s, measured</span>
            </>
          ) : (
            <span className="sval" style={{ left: 0 }}>Run a message above to place your own call here.</span>
          )}
        </div>
        {hasMine && (
          <div className="srow"><span className="slabel">A language model you timed</span>
            <span className="you mine" style={{ left: pos(mySeconds) }} />
            <span className="sval" style={{ left: `calc(${pos(mySeconds)} + 12px)` }}>{mySeconds} s, entered by you</span>
          </div>
        )}
      </div>

      <div className="mine-in">
        <label htmlFor="mine">Timed a language model on a task like this? Enter its seconds per call</label>
        <input id="mine" type="number" min="0.05" max="400" step="0.1" placeholder="e.g. 1.2" value={mine} onChange={(e) => setMine(e.target.value)} />
      </div>

      {slower && (
        <p className="muted small">
          Your call took longer than TypeSafe's 500 ms upper figure. They say their evals run from the West Coast, close to the
          service, so distance from where you are adds time.
        </p>
      )}

      <ul className="points">{speed.claims.map((c, k) => <li key={k}>{c}</li>)}</ul>

      <div className="panel calc">
        <div className="lab-head">
          <label htmlFor="volume">
            Input cost of <b className="amber">{n.toLocaleString()}</b> messages
          </label>
          <input id="volume" type="range" min="0" max={COUNTS.length - 1} value={i} onChange={(e) => setI(+e.target.value)} />
        </div>
        <div className="calc-out">
          <div><span>Jev</span><b className="amber">{money(jev)}</b></div>
          <div><span>Language models, $0.20 to $10 per million tokens</span><b>{money(mtok * lo)} to {money(mtok * hi)}</b></div>
        </div>
        <p className="muted small">
          Counts input tokens only, at {tokens.toLocaleString()} per message
          {result ? " (what your last run used)" : " (typical for the examples)"}. Language-model output tokens would add to their side;
          Jev's output is free. {speed.price_note}
        </p>
      </div>
      <p className="muted small caveat">{speed.caveat}</p>
    </div>
  );
}
