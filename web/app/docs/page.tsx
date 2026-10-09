import Image from "next/image";
import type { Metadata } from "next";
import Link from "next/link";
import CopyCommand from "../components/CopyCommand";
import SiteHeader from "../components/SiteHeader";

export const metadata: Metadata = {
  title: "Documentation",
  description:
    "Install RepoLens, learn the CLI commands and options, and find the right flags for your repository workflow.",
};

const commandGroups = [
  {
    title: "Understand your codebase",
    commands: [
      { name: "analyze", usage: "repolens analyze [OPTIONS]", description: "Scan a repository, map its architecture, and generate documentation.", example: "repolens analyze --path ./my-project --format markdown" },
      { name: "ask", usage: 'repolens ask "QUESTION"', description: "Ask how code works or where to make a specific change.", example: 'repolens ask "Where is authentication handled?"', options: "--path, -p · --no-ai · --verbose, -v" },
      { name: "explain", usage: "repolens explain [TOPIC]", description: "Explain the full architecture or focus on a particular feature.", example: 'repolens explain "payment flow"', options: "--path, -p · --no-ai · --verbose, -v" },
      { name: "find", usage: 'repolens find "QUERY"', description: "Rank matching files, routes, classes, and functions.", example: 'repolens find "user authentication" --top 5', options: "--path, -p · --top, -k · --verbose, -v" },
      { name: "graph", usage: "repolens graph [OPTIONS]", description: "Visualize module relationships or imports for a source file.", example: "repolens graph --file src/app.py", options: "--module, -m · --file, -f · --path, -p · --verbose, -v" },
    ],
  },
  {
    title: "Check, test, and secure",
    commands: [
      { name: "doctor", usage: "repolens doctor [OPTIONS]", description: "Diagnose runtimes, dependencies, configuration, and available tools.", example: "repolens doctor --path .", options: "--path, -p · --verbose, -v" },
      { name: "test", usage: "repolens test [OPTIONS]", description: "Run detected tests, analyze failures, and suggest next steps.", example: "repolens test --timeout 180", options: "--path, -p · --command, -c · --timeout, -t · --verbose, -v" },
      { name: "security", usage: "repolens security [OPTIONS]", description: "Scan for hardcoded secrets and static security risks.", example: "repolens security", options: "--path, -p · --verbose, -v" },
      { name: "api", usage: "repolens api [OPTIONS]", description: "List detected HTTP routes, methods, frameworks, and auth requirements.", example: "repolens api", options: "--path, -p · --verbose, -v" },
    ],
  },
  {
    title: "Set up and inspect",
    commands: [
      { name: "setup", usage: "repolens setup [OPTIONS]", description: "Find project dependency installation steps and offer to run them.", example: "repolens setup", options: "--path, -p · --yes, -y · --verbose, -v" },
      { name: "config", usage: "repolens config [OPTIONS]", description: "View current settings or choose a default AI provider and model.", example: "repolens config --provider ollama --model qwen2.5-coder:latest", options: "--provider · --model · --path, -p" },
      { name: "init", usage: "repolens init [OPTIONS]", description: "Create a starter repolens.toml and .repolensignore in a project.", example: "repolens init --path .", options: "--path, -p" },
      { name: "git", usage: "repolens git [OPTIONS]", description: "Inspect recent commits, the active branch, and development hotspots.", example: "repolens git", options: "--path, -p · --verbose, -v" },
      { name: "onboarding", usage: "repolens onboarding [OPTIONS]", description: "Generate a focused developer onboarding guide.", example: "repolens onboarding --output ./docs", options: "--path, -p · --output, -o · --verbose, -v" },
    ],
  },
];

const analyzeOptions = [
  ["--path, -p PATH", "Repository to scan. Defaults to the current directory."],
  ["--output, -o PATH", "Directory where generated documentation is saved."],
  ["--format, -f FORMAT", "Output format: terminal, markdown, or json."],
  ["--no-ai", "Skip AI reasoning and use deterministic static analysis."],
  ["--llm PROVIDER", "Choose ollama, openai, anthropic, gemini, or groq."],
  ["--model, -m NAME", "Select a model for the configured AI provider."],
  ["--depth, -d INTEGER", "Maximum directory traversal depth."],
  ["--max-file-size BYTES", "Maximum individual file size to analyze."],
  ["--incremental, -i", "Reuse hash-based incremental analysis where available."],
  ["--json", "Output the analysis as structured JSON."],
  ["--verbose, -v", "Show detailed debug logs."],
  ["--force", "Force documentation generation."],
];

const terms = [
  ["Repository path", "The directory RepoLens reads. Use --path to target one; otherwise it uses the current working directory."],
  ["Deterministic analysis", "Static code and graph analysis without an AI provider. Choose it explicitly with --no-ai."],
  ["AI provider", "The optional reasoning backend: Ollama, OpenAI, Anthropic, Gemini, or Groq. Cloud providers may require an API key."],
  ["Output format", "How analysis results are presented: terminal, markdown, or json. Markdown is handy for generated project docs."],
  ["Incremental analysis", "Hash-based analysis mode intended to avoid repeating work for unchanged repository content."],
  ["Traversal depth", "How many nested directory levels to scan. Set --depth when a repository needs a deeper or narrower scan."],
  ["Ignore file", "A .repolensignore file can list directories and patterns that should be skipped."],
];

function CodeBlock({ children }: { children: string }) {
  return (
    <div className="docs-code">
      <code>{children}</code>
      <CopyCommand command={children} />
    </div>
  );
}

export default function DocsPage() {
  return (
    <>
      <SiteHeader />
      <main className="docs-layout page-shell">
        <aside className="docs-sidebar">
          <p className="sidebar-eyebrow">REPOLENS GUIDE</p>
          <a href="#getting-started">Getting started</a>
          <a href="#how-it-works">How RepoLens works</a>
          <p className="sidebar-eyebrow sidebar-spaced">REFERENCE</p>
          <a href="#commands">All commands</a>
          <a href="#analyze-options">Analyze options</a>
          <a href="#keywords">Keywords &amp; concepts</a>
          <a href="#providers">AI providers</a>
          <div className="sidebar-callout">
            <span className="sidebar-callout-icon">↗</span>
            <p>New to RepoLens?</p>
            <Link href="/#install">Start with installation</Link>
          </div>
        </aside>
        <article className="docs-content">
          <div className="docs-breadcrumb"><Link href="/">RepoLens</Link><span>/</span><span>Documentation</span></div>
          <div className="docs-title-block">
            <span className="docs-kicker">DOCUMENTATION</span>
            <h1>Everything you need<br />to <span>read the repo.</span></h1>
            <p>
              Get RepoLens installed, choose the right command, and learn the
              options that help you make sense of any codebase.
            </p>
          </div>

          <section className="docs-section" id="getting-started">
            <p className="docs-section-number">01 / GETTING STARTED</p>
            <h2>Install RepoLens</h2>
            <p>
              RepoLens is a Python CLI. Use Python 3.11 or newer, clone the
              repository, then install it into your environment. Run commands
              from the codebase you want to inspect.
            </p>
            <h3>Windows · PowerShell</h3>
            <CodeBlock>{"git clone https://github.com/kunal-yelgate/repolens.git\ncd repolens\npy -m pip install -e .\ncd ..\\your-project\nrepolens analyze"}</CodeBlock>
            <h3>Linux · macOS · Terminal</h3>
            <CodeBlock>{"git clone https://github.com/kunal-yelgate/repolens.git\ncd repolens\npython3 -m pip install -e .\ncd ../your-project\nrepolens analyze"}</CodeBlock>
            <p className="docs-note">
              A Python virtual environment is recommended. For optional
              integrations, install the extras with{" "}
              <code>pip install -e &quot;.[all]&quot;</code> from the cloned
              RepoLens directory.
            </p>
          </section>

          <section className="docs-section" id="how-it-works">
            <p className="docs-section-number">02 / THE APPROACH</p>
            <h2>Evidence first, explanations second.</h2>
            <p>
              RepoLens scans files and ignores, parses source to extract
              relationships, builds a knowledge graph, and runs detectors for
              frameworks, APIs, data stores, tests, configuration, and security.
              Optional AI reasoning uses that repository context to help explain
              the results.
            </p>
            <div className="docs-pipeline">
              <span>Files</span><i>→</i><span>Parsers</span><i>→</i><span>Knowledge graph</span><i>→</i><span>Reports</span>
            </div>
            <p>
              Start without any AI credentials by running{" "}
              <code>repolens analyze --no-ai</code>. To use a local model,
              install and start Ollama, then select it with <code>--llm ollama</code>
              or configure the default provider.
            </p>
          </section>

          <section className="docs-section" id="commands">
            <p className="docs-section-number">03 / COMMAND REFERENCE</p>
            <h2>Pick a command. Keep moving.</h2>
            <p>
              Run <code>repolens --help</code> for the installed CLI help.
              Commands that accept a repository target support{" "}
              <code>--path</code>; most also support <code>--verbose</code>.
            </p>
            {commandGroups.map((group) => (
              <div className="command-group" key={group.title}>
                <h3>{group.title}</h3>
                <div className="command-list">
                  {group.commands.map((command) => (
                    <article className="command-card" key={command.name}>
                      <div className="command-card-heading">
                        <span className="command-name">repolens {command.name}</span>
                        <span className="command-usage">{command.usage}</span>
                      </div>
                      <p>{command.description}</p>
                      {command.options && <p className="command-options"><span>OPTIONS</span> {command.options}</p>}
                      <CodeBlock>{command.example}</CodeBlock>
                    </article>
                  ))}
                </div>
              </div>
            ))}
          </section>

          <section className="docs-section" id="analyze-options">
            <p className="docs-section-number">04 / OPTIONS</p>
            <h2>Shape your analysis.</h2>
            <p>
              The <code>analyze</code> command accepts these options. Defaults
              for file size and depth can also be set in <code>repolens.toml</code>.
            </p>
            <div className="option-table-wrap">
              <table className="option-table">
                <thead><tr><th>Option</th><th>What it does</th></tr></thead>
                <tbody>
                  {analyzeOptions.map(([option, description]) => (
                    <tr key={option}><td><code>{option}</code></td><td>{description}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3>A few useful combinations</h3>
            <CodeBlock>{"repolens analyze --path ../service --format markdown --output ./docs\nrepolens analyze --no-ai --depth 20 --max-file-size 1000000\nrepolens analyze --llm ollama --model qwen2.5-coder:latest"}</CodeBlock>
          </section>

          <section className="docs-section" id="keywords">
            <p className="docs-section-number">05 / KEYWORDS &amp; CONCEPTS</p>
            <h2>Know what you&apos;re asking for.</h2>
            <p>
              These terms appear throughout the CLI options and generated
              reports. Understanding them makes it easier to tune a scan.
            </p>
            <div className="term-list">
              {terms.map(([term, description]) => (
                <div className="term-row" key={term}>
                  <h3>{term}</h3>
                  <p>{description}</p>
                </div>
              ))}
            </div>
            <h3>Common flag syntax</h3>
            <div className="syntax-grid">
              <div><code>--path ./app</code><span>Long option followed by a value</span></div>
              <div><code>-p ./app</code><span>Short alias for --path</span></div>
              <div><code>--no-ai</code><span>Boolean switch; no value required</span></div>
              <div><code>[OPTIONS]</code><span>Optional flags shown in command help</span></div>
            </div>
          </section>

          <section className="docs-section" id="providers">
            <p className="docs-section-number">06 / AI PROVIDERS</p>
            <h2>Choose how you want to reason.</h2>
            <p>
              Static analysis is available with no provider or API key. For
              model-backed explanations, configure a provider and supply its
              credentials as required by that provider.
            </p>
            <div className="provider-grid">
              <div><span>LOCAL</span><h3>Ollama</h3><p>Run a model on your own machine; configure a model name.</p><code>repolens config --provider ollama --model mistral</code></div>
              <div><span>HOSTED</span><h3>OpenAI · Anthropic · Gemini · Groq</h3><p>Select a provider with <code>--llm</code> and set its API key in the environment.</p><code>repolens analyze --llm openai --model gpt-4o-mini</code></div>
            </div>
            <div className="docs-note docs-note-warning">
              Do not commit API keys. Configure secrets in your local environment
              or your organization&apos;s secret manager.
            </div>
          </section>

          <div className="docs-end-card">
            <div><span className="docs-kicker">READY WHEN YOU ARE</span><h2>Let the repo introduce itself.</h2></div>
            <Link className="button button-primary" href="/#install">Install RepoLens <span aria-hidden="true">↗</span></Link>
          </div>
          <p className="docs-source-note">
            For the latest option list, run <code>repolens analyze --help</code>.
            Browse the project source and releases on{" "}
            <a href="https://github.com/kunal-yelgate/repolens" rel="noreferrer" target="_blank">GitHub ↗</a>.
          </p>
        </article>
      </main>
      <footer className="site-footer page-shell">
        <Link aria-label="RepoLens home" className="brand" href="/">
          <Image
            alt=""
            aria-hidden="true"
            className="brand-logo"
            height={32}
            src="/repolens-logo.png"
            width={32}
          />
        </Link>
        <span>Understand the code. Ship with context.</span>
        <div><Link href="/">Home</Link><a href="https://github.com/kunal-yelgate/repolens" rel="noreferrer" target="_blank">GitHub ↗</a></div>
      </footer>
    </>
  );
}
