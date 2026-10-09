import { Link } from "react-router-dom";
import MiniFlow from "../components/MiniFlow.jsx";

function Card({ u }) {
  const ready = u.status === "ready";
  const body = (
    <>
      <div className="pcard-diagram">
        <MiniFlow rows={u.diagram} />
      </div>
      <div className="pcard-body">
        <div className="pcard-top">
          <span className="num">{String(u.number).padStart(2, "0")}</span>
          <span className={`pill ${u.status}`}>{ready ? "Ready" : "Coming soon"}</span>
        </div>
        <h3>{u.title}</h3>
        <p className="muted">{u.summary}</p>
        <ul className="pcard-points">
          {u.highlights.map((h) => <li key={h}>{h}</li>)}
        </ul>
        {ready && <span className="pcard-open">Open playground</span>}
      </div>
    </>
  );
  return ready ? (
    <Link to={`/${u.slug}`} className="pcard">{body}</Link>
  ) : (
    <div className="pcard off">{body}</div>
  );
}

export default function Home({ usecases }) {
  return (
    <>
      <section className="home-hero">
        <h1>Playgrounds for a model that decides</h1>
        <p className="lead">
          Jev answers fixed questions about text with probabilities instead of writing sentences. Each playground below is a hands-on
          demo of one idea. Pick one to start.
        </p>
      </section>
      <div className="pcards">
        {usecases.map((u) => <Card key={u.slug} u={u} />)}
      </div>
    </>
  );
}
