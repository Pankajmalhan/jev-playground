// The workflow drawn as a graph. Nodes and arrows light up as the run reaches them.
// `trail` is the list of nodes visited, in order; `waiting` is true while a person is asked.

const NODES = {
  message:      { x: 10,  y: 180, w: 120, h: 60,  label: "Message",      sub: "from the customer" },
  supervisor:   { x: 200, y: 140, w: 170, h: 120, label: "Supervisor",   sub: "Jev decides who acts next", jev: true },
  billing:      { x: 520, y: 56,  w: 170, h: 52,  label: "Billing agent",   sub: "lookup, refund" },
  shipping:     { x: 520, y: 140, w: 170, h: 52,  label: "Shipping agent",  sub: "track an order" },
  technical:    { x: 520, y: 224, w: 170, h: 52,  label: "Technical agent", sub: "search help" },
  finalize:     { x: 780, y: 180, w: 160, h: 60,  label: "Verify and reply", sub: "Jev checks the reply", jev: true },
  human_review: { x: 200, y: 350, w: 170, h: 58,  label: "Human review", sub: "a person decides", dashed: true },
};

const EDGES = [
  { id: "msg",      d: "M130 210 L200 210" },
  { id: "billing",  d: "M370 185 L520 82" },
  { id: "shipping", d: "M370 200 L520 166" },
  { id: "technical",d: "M370 215 L520 250" },
  { id: "return",   d: "M600 296 C600 332 345 332 345 262", label: ["reports back", 470, 326] },
  { id: "human",    d: "M250 260 L250 350", label: ["not sure, or sensitive", 258, 310], anchor: "start" },
  { id: "pick",     d: "M370 379 L660 379 L660 298", label: ["the person picks the team", 520, 372] },
  { id: "final",    d: "M285 140 L285 14 L860 14 L860 180", label: ["done", 570, 8] },
];

const AGENTS = ["billing", "shipping", "technical"];

// Which arrows have been used, from the order the nodes were visited.
function litEdges(trail) {
  const lit = new Set();
  const t = ["message", ...trail];
  for (let i = 1; i < t.length; i++) {
    const a = t[i - 1], b = t[i];
    if (a === "message") lit.add("msg");
    else if (a === "supervisor" && AGENTS.includes(b)) lit.add(b);
    else if (AGENTS.includes(a) && b === "supervisor") lit.add("return");
    else if (a === "supervisor" && b === "human_review") lit.add("human");
    else if (a === "human_review" && AGENTS.includes(b)) lit.add("pick");
    else if (b === "finalize") lit.add("final");
  }
  return lit;
}

export default function AgentGraph({ trail, running, waiting }) {
  const visited = new Set(trail);
  const last = trail[trail.length - 1];
  const edges = litEdges(trail);

  return (
    <div className="agraph-wrap">
      <svg className="agraph" viewBox="0 0 960 424" role="img" aria-label="The workflow: a message goes to the Jev supervisor, which picks a specialist; specialists report back; Jev finishes by checking the reply, or a person is asked.">
        <defs>
          <marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M0 0 L10 5 L0 10 z" fill="context-stroke" />
          </marker>
        </defs>

        <rect className="agroup" x="500" y="34" width="210" height="262" rx="12" />
        <text className="agroup-t" x="514" y="26">Specialists</text>

        {EDGES.map((e) => (
          <g key={e.id}>
            <path className={`aedge${edges.has(e.id) ? " lit" : ""}${e.id === "pick" || e.id === "human" ? " dash" : ""}`} d={e.d} markerEnd="url(#ah)" />
            {e.label && <text className="alabel" x={e.label[1]} y={e.label[2]} textAnchor={e.anchor || "middle"}>{e.label[0]}</text>}
          </g>
        ))}

        {Object.entries(NODES).map(([id, n]) => {
          const cls = ["anode", n.jev && "jev", n.dashed && "dashed", visited.has(id) && "lit",
            id === last && running && !(id === "human_review" && waiting) && "cur", id === "human_review" && waiting && "wait"].filter(Boolean).join(" ");
          return (
            <g key={id} className={cls}>
              <rect x={n.x} y={n.y} width={n.w} height={n.h} rx="10" />
              <text className="an-t" x={n.x + n.w / 2} y={n.y + n.h / 2 - 3} textAnchor="middle">{n.label}</text>
              <text className="an-s" x={n.x + n.w / 2} y={n.y + n.h / 2 + 15} textAnchor="middle">{n.sub}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
