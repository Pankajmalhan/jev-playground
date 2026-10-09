// One place for every call to the backend. Each use case adds its own helpers
// below, so pages never build URLs by hand.

async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.error || body.detail || `Request failed (${res.status})`);
  return body;
}

const get = (path) => request(path);

// For endpoints that stream one JSON object per line. onEvent is called as each line arrives.
async function stream(path, data, onEvent) {
  const res = await fetch(`/api${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || body.detail || `Request failed (${res.status})`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let i;
    while ((i = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, i).trim();
      buffer = buffer.slice(i + 1);
      if (line) onEvent(JSON.parse(line));
    }
  }
}
const post = (path, data) => request(path, { method: "POST", body: JSON.stringify(data) });

export const api = {
  health: () => get("/health"),
  usecases: () => get("/usecases"),

  // 1 - what is jev
  whatIsJev: {
    guide: () => get("/what-is-jev/guide"),
    examples: () => get("/what-is-jev/examples"),
    analyze: (text) => post("/what-is-jev/analyze", { text }),
    batch: () => post("/what-is-jev/batch", {}),
    history: () => get("/what-is-jev/history"),
  },

  // 2 - jev vs llm vs agent
  jevVsLlm: {
    guide: () => get("/jev-vs-llm-vs-agents/guide"),
    examples: () => get("/jev-vs-llm-vs-agents/examples"),
    orders: () => get("/jev-vs-llm-vs-agents/orders"),
    ask: (lane, text, withOrder) => post(`/jev-vs-llm-vs-agents/ask/${lane}`, { text, with_order: withOrder }),
  },

  // 3 - jev as supervisor
  supervisor: {
    guide: () => get("/jev-supervisor/guide"),
    examples: () => get("/jev-supervisor/examples"),
    orders: () => get("/jev-supervisor/orders"),
    run: (text, onEvent) => stream("/jev-supervisor/run", { text }, onEvent),
    resume: (threadId, choice, onEvent) => stream("/jev-supervisor/resume", { thread_id: threadId, choice }, onEvent),
  },

  // 4 - score a whole table
  table: {
    guide: () => get("/score-a-table/guide"),
    run: (size, onEvent) => stream("/score-a-table/run", { size }, onEvent),
  },

  // 5 - guard the agent
  guard: {
    guide: () => get("/guard-the-agent/guide"),
    scenarios: () => get("/guard-the-agent/scenarios"),
    run: (lane, text, hardRule) => post(`/guard-the-agent/run/${lane}`, { text, hard_rule: hardRule }),
    stress: (runs, hardRule, onEvent) => stream("/guard-the-agent/stress", { runs, hard_rule: hardRule }, onEvent),
  },

  // 6 - moderation and calibration
  moderation: {
    guide: () => get("/moderation-lab/guide"),
    run: () => post("/moderation-lab/run", {}),
    tryOne: (text) => post("/moderation-lab/try", { text }),
  },

  // 7 - model router
  router: {
    guide: () => get("/model-router/guide"),
    run: (onEvent) => stream("/model-router/run", {}, onEvent),
  },

  // 8 - decisions from structured data
  decisions: {
    guide: () => get("/structured-decisions/guide"),
    examples: () => get("/structured-decisions/examples"),
    batch: (policy, calculate) => post("/structured-decisions/batch", { policy, calculate }),
    decide: (expense, policy, calculate) => post("/structured-decisions/decide", { expense, policy, calculate }),
  },

  // 9 - grounded answers
  grounded: {
    guide: () => get("/grounded-answers/guide"),
    questions: () => get("/grounded-answers/questions"),
    ask: (lane, question, strict) => post(`/grounded-answers/ask/${lane}`, { question, strict }),
    runAll: (strict, onEvent) => stream("/grounded-answers/run-all", { strict }, onEvent),
  },
};
