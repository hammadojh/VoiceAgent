# Deploying Miso TTS 8B on Modal

`modal_app.py` serves the [Miso TTS 8B](https://github.com/MisoLabsAI/MisoTTS)
model (`MisoLabs/MisoTTS`) on a GPU via [Modal](https://modal.com).

> **Why this isn't already deployed:** this repo's Claude Code *web* session runs
> in an environment whose **network policy blocks outbound traffic to
> `api.modal.com`** (verified: `pypi.org` → 200, `modal.com` → 403). `modal deploy`
> needs to reach Modal's servers, so it can't run from that sandbox. Run the steps
> below from your own machine — or from a Claude Code environment created with a
> network policy that allows `modal.com` — and it deploys end to end.

## Prerequisites

```bash
pip install modal
modal token set --token-id <YOUR_ID> --token-secret <YOUR_SECRET>
```

> 🔐 Rotate any token you've shared in plaintext (modal.com → Settings → API Tokens).
> No token is stored in this repo; the CLI keeps it in `~/.modal.toml`.

## Smoke test (one generation, saves `hello.wav` locally)

```bash
modal run modal_app.py
# or with custom text:
modal run modal_app.py --text "Miso emotes like a human and replies in 110 milliseconds."
```

## Deploy the service

```bash
modal deploy modal_app.py
```

Modal builds the image (installs the torch 2.4 stack + the MisoTTS package and
**bakes the model weights into the image**), then prints a public URL for the
`tts` endpoint.

## Use the HTTP endpoint

```bash
curl -G "https://<your-workspace>--miso-tts-tts.modal.run" \
     --data-urlencode "text=Hello from Miso, deployed on Modal." \
     --data-urlencode "speaker=0" \
     --data-urlencode "max_ms=10000" \
     -o out.wav
```

Interactive docs are available at the endpoint URL + `/docs` (Swagger UI).

## Call it from other Python / Modal code

```python
import modal
MisoTTS = modal.Cls.from_name("miso-tts", "MisoTTS")
wav_bytes = MisoTTS().generate.remote(text="Hi there", speaker=0, max_ms=10_000)
open("out.wav", "wb").write(wav_bytes)
```

## Notes & knobs

- **GPU:** defaults to `A100` (40 GB) — plenty for ~8B in `bfloat16`. Set
  `GPU = "L40S"` or `"H100"` in `modal_app.py` to trade cost/latency.
- **Cold start:** weights are baked into the image, so the first request only
  pays model-load time, not a multi-GB download.
- **Idle scale-down:** container stays warm 5 min after the last request
  (`scaledown_window=300`), then releases the GPU so you stop paying.
- **Gated weights:** `MisoLabs/MisoTTS` is public. If it ever becomes gated, add a
  Hugging Face token as a Modal secret and pass it to `_download_weights`.
