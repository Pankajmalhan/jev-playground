// Three bars of different heights: a tiny probability distribution.
export default function Mark() {
  return (
    <svg className="brand-mark" viewBox="0 0 24 24" aria-hidden="true">
      <rect x="3" y="11" width="5" height="10" rx="1.5" fill="var(--sea)" />
      <rect x="10" y="3" width="5" height="18" rx="1.5" fill="var(--amber)" />
      <rect x="17" y="14" width="5" height="7" rx="1.5" fill="var(--sea)" opacity="0.6" />
    </svg>
  );
}
