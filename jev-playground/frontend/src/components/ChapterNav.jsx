import { useEffect, useState } from "react";

// A sticky strip of anchors that follows the reader down a long page.
export default function ChapterNav({ chapters }) {
  const [current, setCurrent] = useState(chapters[0]?.id);

  useEffect(() => {
    const seen = new Map();
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => seen.set(e.target.id, e.isIntersecting ? e.boundingClientRect.top : null));
        const visible = [...seen.entries()].filter(([, top]) => top !== null).sort((a, b) => a[1] - b[1]);
        if (visible.length) setCurrent(visible[0][0]);
      },
      { rootMargin: "-80px 0px -55% 0px" }
    );
    chapters.forEach((c) => {
      const el = document.getElementById(c.id);
      if (el) io.observe(el);
    });
    return () => io.disconnect();
  }, [chapters]);

  return (
    <nav className="chapters" aria-label="On this page">
      {chapters.map((c) => (
        <a key={c.id} href={`#${c.id}`} className={current === c.id ? "on" : ""}>
          {c.label}
        </a>
      ))}
    </nav>
  );
}
