<div align="center">

<img src="public/repolens-logo.png" alt="RepoLens logo" width="160" />

# RepoLens website

</div>

This is the Next.js website for RepoLens.

## Deploy to Vercel

Import the `kunal-yelgate/repolens` repository in Vercel and set the project
Root Directory to `web`. Keep the detected Next.js framework settings and leave
the output directory unset. The project has no required environment variables.

Vercel can also deploy it from the repository root with its CLI:

```bash
npx vercel --cwd web
npx vercel --prod --cwd web
```

The first command links the local project and creates a preview deployment; the
second publishes to production. Vercel project-link metadata is kept out of Git
by the repository's `.gitignore`.
