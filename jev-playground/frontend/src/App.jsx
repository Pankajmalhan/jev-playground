import { Suspense, useEffect, useState } from "react";
import { Route, Routes, useParams } from "react-router-dom";
import { api } from "./api.js";
import HomeLayout from "./components/HomeLayout.jsx";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import { pages } from "./pages/registry.js";

// A playground page is found by slug. The backend decides which playgrounds exist;
// `pages` decides which component draws each one.
function UseCaseRoute({ usecases }) {
  const { slug } = useParams();
  const usecase = usecases.find((u) => u.slug === slug);
  const Page = pages[slug];
  if (!usecase || !Page) return <div className="panel">No such page: {slug}</div>;
  return (
    <Suspense fallback={<div className="muted">Loading...</div>}>
      <Page usecase={usecase} />
    </Suspense>
  );
}

export default function App() {
  const [usecases, setUsecases] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.usecases().then((d) => setUsecases(d.usecases)).catch((e) => setError(e.message));
  }, []);

  return (
    <Routes>
      {/* the dashboard: no menu */}
      <Route index element={<HomeLayout error={error}><Home usecases={usecases} /></HomeLayout>} />
      {/* a playground: menu on the left, the playground on the right */}
      <Route element={<Layout usecases={usecases} error={error} />}>
        <Route path=":slug" element={<UseCaseRoute usecases={usecases} />} />
      </Route>
    </Routes>
  );
}
