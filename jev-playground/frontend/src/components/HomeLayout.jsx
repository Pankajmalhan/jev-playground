import { Link } from "react-router-dom";
import Mark from "./Mark.jsx";

// The layout for the home page: no menu, just the dashboard.
export default function HomeLayout({ error, children }) {
  return (
    <div className="home">
      <header className="home-bar">
        <Link to="/" className="brand">
          <Mark />
          Jev Playground
        </Link>
      </header>
      <main>
        {error && <div className="panel error">Cannot reach the API: {error}</div>}
        {children}
      </main>
    </div>
  );
}
