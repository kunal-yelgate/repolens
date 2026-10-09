import Image from "next/image";
import Link from "next/link";

export default function SiteHeader() {
  return (
    <header className="site-header">
      <Link aria-label="RepoLens home" className="brand" href="/">
        <Image
          alt=""
          aria-hidden="true"
          className="brand-logo"
          height={48}
          src="/repolens-logo.png"
          width={48}
        />
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
