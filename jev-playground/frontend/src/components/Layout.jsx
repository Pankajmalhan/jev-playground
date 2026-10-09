import { Link, NavLink, Outlet } from "react-router-dom";
import Mark from "./Mark.jsx";

// The layout for a playground page: the menu on the left, the playground on the right.
export default function Layout({ usecases, error }) {
  return (
    <div className="shell">
      <aside className="rail">
        <Link to="/" className="brand">
          <Mark />
          Jev Playground
        </Link>
        <nav className="nav" aria-label="Playgrounds">
          <Link to="/" className="nav-home">
            <svg viewBox="0 0 16 16" aria-hidden="true">
              <rect x="1.5" y="1.5" width="5.5" height="5.5" rx="1.2" /><rect x="9" y="1.5" width="5.5" height="5.5" rx="1.2" />
              <rect x="1.5" y="9" width="5.5" height="5.5" rx="1.2" /><rect x="9" y="9" width="5.5" height="5.5" rx="1.2" />
            </svg>
            All playgrounds
          </Link>
          {usecases.map((u) => (
            <NavLink
              key={u.slug}
              to={`/${u.slug}`}
              className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
              title={u.tagline}
            >
              <span className="num">{String(u.number).padStart(2, "0")}</span>
              {u.title}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main>
        {error && <div className="panel error">Cannot reach the API: {error}</div>}
        <Outlet />
      </main>
    </div>
  );
}
