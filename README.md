# Miso Labs — Landing Page

A minimal, zero-dependency recreation of [misolabs.ai](https://www.misolabs.ai) —
the most emotive foundation models for voice.

Content sourced from the official model repo: [MisoLabsAI/MisoTTS](https://github.com/MisoLabsAI/MisoTTS).

## What's here

- **`index.html`** — the entire site. One self-contained file with inline CSS. No build step, no framework, no dependencies.
- **`.github/workflows/deploy.yml`** — deploys the static site to GitHub Pages on every push to `main`.

## Deploy (minimal setup)

This is as minimal as a deploy gets — a single static file served by GitHub Pages.

1. **One-time:** in the repo, open **Settings → Pages → Build and deployment → Source** and pick **GitHub Actions**.
2. Push to the repository (or merge to `main`).
3. The **Deploy to GitHub Pages** workflow runs automatically and the site goes live at `https://<owner>.github.io/<repo>/` — for this repo, `https://hammadojh.github.io/VoiceAgent/`.

> The workflow tries to enable Pages itself (`actions/configure-pages` with `enablement: true`),
> but GitHub only lets the Actions token create the Pages site when an admin has allowed it.
> If you see `Resource not accessible by integration`, do the one-time **Source → GitHub Actions**
> step above and re-run the workflow — every push deploys automatically after that.

## Run locally

It's just a static file. Open `index.html` in a browser, or serve it:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```
