import Link from "next/link";

export default function SiteHeader() {
  return (
    <header className="site-header">
      <Link aria-label="RepoLens home" className="brand" href="/">
        <span aria-hidden="true" className="brand-mark">
          <svg viewBox="0 0 36 36" fill="none">
            <path
              d="M5 25.5 13.6 17l5.2 5.1L30.5 10"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2.4"
            />
            <path
              d="M22.7 10h7.8v7.8"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2.4"
            />
          </svg>
        </span>
        <span>repo<span className="brand-accent">lens</span></span>
      </Link>
      <nav aria-label="Main navigation" className="main-nav">
        <Link href="/#features">Features</Link>
        <Link href="/#install">Install</Link>
        <Link href="/#workflow">Workflow</Link>
        <Link href="/docs">Docs</Link>
      </nav>
      <a
        className="header-github"
        href="https://github.com/kunal-yelgate/repolens"
        rel="noreferrer"
        target="_blank"
      >
        <span>GitHub</span>
        <span aria-hidden="true">↗</span>
      </a>
    </header>
  );
}
