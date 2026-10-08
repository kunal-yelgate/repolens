import Link from "next/link";
import CopyCommand from "./components/CopyCommand";
import SiteHeader from "./components/SiteHeader";

const features = [
  {
    number: "01",
    title: "Understand the moving parts",
    description:
      "Discover languages, frameworks, entry points, routes, data models, environment variables, and project commands from source evidence.",
    icon: "◫",
  },
  {
    number: "02",
    title: "Follow how code connects",
    description:
      "Build a repository knowledge graph to see imports, dependencies, and module relationships instead of guessing from folder names.",
    icon: "⌘",
  },
  {
    number: "03",
    title: "Get useful docs, automatically",
    description:
      "Generate architecture, setup, testing, API, onboarding, and project overview documents from the repository you actually have.",
    icon: "▤",
  },
  {
    number: "04",
    title: "Keep your code on your machine",
    description:
      "Run deterministic static analysis locally. Add a supported AI provider when you want richer explanations; Ollama can stay local.",
    icon: "⌂",
  },
];

const workflow = [
  ["Scan", "Inventory source files while respecting ignore rules and file-size limits."],
  ["Connect", "Parse code and assemble a graph of modules, symbols, and relationships."],
  ["Explain", "Use verified repository context for reports, questions, and code search."],
  ["Share", "Give teammates generated docs they can use to get oriented faster."],
];

const docs = [
  "REPOLENS.md",
  "ARCHITECTURE.md",
  "SETUP.md",
  "TESTING.md",
  "API.md",
  "ONBOARDING.md",
];

const terminalLines = [
  ["$ repolens analyze", "terminal-command"],
  ["", ""],
  ["  SCANNING  ./acme-platform", "terminal-muted"],
  ["  ├─ 248 files indexed", "terminal-default"],
  ["  ├─ TypeScript · Python · SQL", "terminal-default"],
  ["  ├─ Next.js · FastAPI · PostgreSQL", "terminal-default"],
  ["  └─ 3 API routes · 12 entry points", "terminal-default"],
  ["", ""],
  ["  PROJECT MAP READY", "terminal-success"],
  ["  → REPOLENS.md", "terminal-file"],
  ["  → ARCHITECTURE.md", "terminal-file"],
  ["  → SETUP.md", "terminal-file"],
  ["  → ONBOARDING.md", "terminal-file"],
];

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="section-label">
      <span aria-hidden="true" className="label-line" />
      {children}
    </p>
  );
}

function InstallCard({
  title,
  command,
  note,
  platform,
}: {
  title: string;
  command: string;
  note: string;
  platform: string;
}) {
  return (
    <article className="install-card">
      <div className="install-card-top">
        <span aria-hidden="true" className="platform-mark">{platform}</span>
        <div>
          <p className="eyebrow">INSTALL ON</p>
          <h3>{title}</h3>
        </div>
      </div>
      <p className="install-note">{note}</p>
      <div className="code-block">
        <code>{command}</code>
        <CopyCommand command={command} />
      </div>
    </article>
  );
}

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main>
        <section className="hero page-shell">
          <div className="hero-copy">
            <div className="availability">
              <span className="pulse-dot" />
              OPEN SOURCE · BUILT FOR YOUR TERMINAL
            </div>
            <h1>
              New codebase?
              <br />
              <span>Get the whole picture.</span>
            </h1>
            <p className="hero-description">
              RepoLens turns an unfamiliar repository into a map your team can
              actually use — architecture, dependencies, commands, and
              onboarding docs, all from one local-first CLI.
            </p>
            <div className="hero-actions">
              <Link className="button button-primary" href="#install">
                Get started <span aria-hidden="true">↓</span>
              </Link>
              <Link className="button button-secondary" href="/docs">
                Explore the docs <span aria-hidden="true">↗</span>
              </Link>
            </div>
            <div className="hero-meta">
              <span><i aria-hidden="true" /> Python 3.11+</span>
              <span><i aria-hidden="true" /> Windows, macOS &amp; Linux</span>
              <span><i aria-hidden="true" /> MIT licensed</span>
            </div>
          </div>
          <div aria-label="Example RepoLens terminal analysis" className="terminal-window">
            <div className="terminal-titlebar">
              <div aria-hidden="true" className="window-dots"><i /><i /><i /></div>
              <span>repolens — project overview</span>
              <span className="terminal-live"><i /> LIVE</span>
            </div>
            <div className="terminal-body">
              {terminalLines.map(([line, className], index) => (
                <p className={className} key={`${line}-${index}`}>
                  {line || "\u00a0"}
                </p>
              ))}
              <span aria-hidden="true" className="terminal-cursor" />
            </div>
            <div className="terminal-footer">
              <span><i /> STATIC ANALYSIS COMPLETE</span>
              <span>100% LOCAL</span>
            </div>
          </div>
          <div aria-hidden="true" className="hero-grid" />
          <div aria-hidden="true" className="hero-glow" />
        </section>

        <section aria-label="Project highlights" className="proof-strip">
          <div className="proof-inner page-shell">
            <p>BUILT FOR THE MOMENT AFTER <span>git clone</span></p>
            <div><strong>10+</strong><span>languages</span></div>
            <div><strong>6</strong><span>generated guides</span></div>
            <div><strong>0</strong><span>code uploads required</span></div>
          </div>
        </section>

        <section className="section page-shell" id="features">
          <div className="section-heading">
            <div>
              <SectionLabel>WHY REPOLENS</SectionLabel>
              <h2>Go from code scattered<br />across folders to <span>clear answers.</span></h2>
            </div>
            <p>
              Skip the hours of clicking through files. Start with a grounded
              overview, then drill into exactly what your project needs.
            </p>
          </div>
          <div className="feature-grid">
            {features.map((feature) => (
              <article className="feature-card" key={feature.number}>
                <div className="feature-card-top">
                  <span className="feature-icon">{feature.icon}</span>
                  <span className="feature-number">{feature.number}</span>
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                <span aria-hidden="true" className="card-arrow">↗</span>
              </article>
            ))}
          </div>
        </section>

        <section className="workflow-section" id="workflow">
          <div className="page-shell workflow-layout">
            <div className="workflow-intro">
              <SectionLabel>A CLEARER START</SectionLabel>
              <h2>One command.<br /><span>A working map.</span></h2>
              <p>
                RepoLens combines static code analysis with optional AI
                reasoning. Evidence comes first, so generated guidance stays
                connected to your actual repository.
              </p>
              <Link className="text-link" href="/docs#how-it-works">
                See how it works <span aria-hidden="true">→</span>
              </Link>
            </div>
            <div className="workflow-list">
              {workflow.map(([title, description], index) => (
                <article className="workflow-step" key={title}>
                  <div className="step-index">
                    <span>0{index + 1}</span>
                    {index < workflow.length - 1 && <i />}
                  </div>
                  <div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section install-section page-shell" id="install">
          <div className="section-heading">
            <div>
              <SectionLabel>QUICK START</SectionLabel>
              <h2>At home in <span>your terminal.</span></h2>
            </div>
            <p>
              Requires Python 3.11 or newer. Install from the project source,
              then run RepoLens from the repository you want to explore.
            </p>
          </div>
          <div className="install-grid">
            <InstallCard
              title="Windows"
              command={"py -m pip install -e ."}
              note="Clone the project, open PowerShell in its folder, and install RepoLens."
              platform="⊞"
            />
            <InstallCard
              title="Linux / macOS"
              command={"python3 -m pip install -e ."}
              note="Clone the project, open a terminal in its folder, and install RepoLens."
              platform="⌘"
            />
          </div>
          <div className="install-followup">
            <div className="followup-title">
              <span className="followup-check">✓</span>
              <div>
                <strong>Now analyze a repository</strong>
                <span>Run this from the project folder you want to understand.</span>
              </div>
            </div>
            <div className="code-block code-block-wide">
              <code>repolens analyze</code>
              <CopyCommand command="repolens analyze" />
            </div>
          </div>
          <p className="install-extra">
            Want optional AI providers or Git history analysis? Install extras with{" "}
            <code>pip install -e &quot;.[all]&quot;</code>. No provider key is needed
            for deterministic static analysis.
          </p>
        </section>

        <section className="usecase-section">
          <div className="page-shell usecase-layout">
            <div className="usecase-copy">
              <SectionLabel>MADE FOR REAL WORK</SectionLabel>
              <h2>Your first hour<br />in a new repo, <span>rewritten.</span></h2>
              <p>
                Join a team, pick up a legacy service, or review an unfamiliar
                project. Use RepoLens to orient yourself before you change
                anything.
              </p>
              <Link className="button button-primary" href="/docs#commands">
                Find your command <span aria-hidden="true">↗</span>
              </Link>
            </div>
            <div className="usecase-terminal">
              <div className="usecase-terminal-label"><span>YOUR TERMINAL</span><span>~/new-project</span></div>
              <div className="work-command"><span>01</span><code>repolens doctor</code><p>Check runtimes, tools, and project setup</p></div>
              <div className="work-command"><span>02</span><code>repolens analyze</code><p>Generate your architectural map and docs</p></div>
              <div className="work-command"><span>03</span><code>repolens ask &quot;Where does auth start?&quot;</code><p>Trace a question to relevant parts of the codebase</p></div>
              <div className="work-command"><span>04</span><code>repolens find &quot;user session&quot;</code><p>Rank matching files, routes, and symbols</p></div>
            </div>
          </div>
        </section>

        <section className="docs-preview section page-shell">
          <div className="section-heading">
            <div>
              <SectionLabel>WHAT YOU GET</SectionLabel>
              <h2>Useful context, ready<br />to <span>share with the team.</span></h2>
            </div>
            <p>
              Every report is generated from the repository RepoLens scanned.
              Keep the Markdown files in your project or pass them to your team.
            </p>
          </div>
          <div className="doc-file-list">
            {docs.map((file, index) => (
              <div className="doc-file" key={file}>
                <span className="doc-file-icon">MD</span>
                <span>{file}</span>
                <span className="doc-file-purpose">
                  {["Overview", "System design", "Setup guide", "Test strategy", "HTTP routes", "New developer guide"][index]}
                </span>
                <span aria-hidden="true" className="doc-file-arrow">↗</span>
              </div>
            ))}
          </div>
          <Link className="text-link docs-preview-link" href="/docs">
            Read the command reference <span aria-hidden="true">→</span>
          </Link>
        </section>

        <section className="final-cta page-shell">
          <div aria-hidden="true" className="cta-orb" />
          <SectionLabel>YOUR NEXT REPO IS ALREADY WAITING</SectionLabel>
          <h2>Get oriented.<br /><span>Then get building.</span></h2>
          <div className="cta-actions">
            <Link className="button button-primary" href="#install">
              Install RepoLens <span aria-hidden="true">↓</span>
            </Link>
            <Link className="button button-secondary" href="/docs">
              Browse documentation <span aria-hidden="true">↗</span>
            </Link>
          </div>
        </section>
      </main>
      <footer className="site-footer page-shell">
        <Link aria-label="RepoLens home" className="brand" href="/">
          <span aria-hidden="true" className="brand-mark">
            <svg viewBox="0 0 36 36" fill="none">
              <path d="M5 25.5 13.6 17l5.2 5.1L30.5 10" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.4" />
              <path d="M22.7 10h7.8v7.8" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.4" />
            </svg>
          </span>
          <span>repo<span className="brand-accent">lens</span></span>
        </Link>
        <span>Understand the code. Ship with context.</span>
        <div>
          <Link href="/docs">Documentation</Link>
          <a href="https://github.com/kunal-yelgate/repolens" rel="noreferrer" target="_blank">GitHub ↗</a>
        </div>
      </footer>
    </>
  );
}
