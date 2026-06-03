# Miso Labs — Landing Page

A minimal, zero-dependency recreation of [misolabs.ai](https://www.misolabs.ai) —
the most emotive foundation models for voice.

Content sourced from the official model repo: [MisoLabsAI/MisoTTS](https://github.com/MisoLabsAI/MisoTTS).

## What's here

- **`index.html`** — the entire site. One self-contained file with inline CSS. No build step, no framework, no dependencies.
- **`.github/workflows/deploy.yml`** — deploys the static site to GitHub Pages on every push to `main`.

## Deploy (minimal setup)

This is as minimal as a deploy gets — a single static file served by GitHub Pages.

1. Push to the repository (or merge to `main`).
2. The **Deploy to GitHub Pages** workflow runs automatically and enables Pages on first run.
3. The site goes live at `https://<owner>.github.io/<repo>/`.

> The workflow uses `actions/configure-pages` with `enablement: true`, so GitHub Pages
> is turned on automatically — no manual repo settings required (assuming Actions has
> Pages write permission for the repo).

## Run locally

It's just a static file. Open `index.html` in a browser, or serve it:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```
