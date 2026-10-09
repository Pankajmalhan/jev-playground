// An amber note: a title and a few short paragraphs.
export default function Callout({ title, body }) {
  return (
    <div className="callout">
      <h3>{title}</h3>
      {body.map((p, i) => <p key={i}>{p}</p>)}
    </div>
  );
}
