"""
Deploy the Miso TTS 8B model (https://github.com/MisoLabsAI/MisoTTS) on Modal.

The model weights (`MisoLabs/MisoTTS`, ~8B backbone + 300M decoder) are baked
into the container image at build time so cold starts don't re-download them.

Auth: Modal reads your credentials from the local CLI config / env vars at
deploy time — no token is stored in this file.

    pip install modal
    modal token set --token-id <id> --token-secret <secret>   # one time

Quick smoke test (runs the model once, writes hello.wav locally):
    modal run modal_app.py

Deploy the HTTP + callable service:
    modal deploy modal_app.py

After deploy, Modal prints a public URL for `tts`. Call it like:
    curl -G "https://<your-workspace>--miso-tts-tts.modal.run" \
         --data-urlencode "text=Hello from Miso, deployed on Modal." \
         -o out.wav
"""

import io
import modal

# Pinned to the model repo's own pyproject.toml so the runtime matches upstream.
MODEL_REPO = "MisoLabs/MisoTTS"
MODEL_DIR = "/model"
GPU = "A100"  # 8B in bf16 needs ~16GB+; A100-40GB is comfortable. "L40S" also works.

app = modal.App("miso-tts")


def _download_weights():
    """Runs at image build time — snapshot the HF weights into the image."""
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=MODEL_REPO, local_dir=MODEL_DIR)


image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg")
    # Match upstream's exact torch stack, then install the model package from git
    # (this pulls moshi, torchtune, torchao, bitsandbytes, silentcipher, etc.).
    .pip_install("torch==2.4.0", "torchaudio==2.4.0", index_url="https://download.pytorch.org/whl/cu121")
    .pip_install("huggingface_hub==0.28.1", "fastapi[standard]")
    .pip_install("git+https://github.com/MisoLabsAI/MisoTTS.git")
    .run_function(_download_weights)
)


@app.cls(gpu=GPU, image=image, timeout=600, scaledown_window=300)
class MisoTTS:
    @modal.enter()
    def load(self):
        import torch
        from generator import load_miso_8b

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # load_miso_8b accepts a local path or an HF repo id — we pass the baked path.
        self.generator = load_miso_8b(
            device=self.device, model_path_or_repo_id=MODEL_DIR
        )
        self.sample_rate = self.generator.sample_rate

    def _synthesize(self, text: str, speaker: int, max_ms: int) -> bytes:
        import torchaudio

        audio = self.generator.generate(
            text=text,
            speaker=speaker,
            context=[],
            max_audio_length_ms=max_ms,
        )
        buf = io.BytesIO()
        torchaudio.save(buf, audio.unsqueeze(0).cpu(), self.sample_rate, format="wav")
        return buf.getvalue()

    @modal.method()
    def generate(self, text: str, speaker: int = 0, max_ms: int = 10_000) -> bytes:
        """Callable from other Modal code or `.remote()`; returns WAV bytes."""
        return self._synthesize(text, speaker, max_ms)

    @modal.fastapi_endpoint(method="GET", docs=True)
    def tts(self, text: str, speaker: int = 0, max_ms: int = 10_000):
        """Public HTTP endpoint: GET ?text=...&speaker=0&max_ms=10000 -> audio/wav."""
        from fastapi import Response

        wav = self._synthesize(text, speaker, max_ms)
        return Response(content=wav, media_type="audio/wav")


@app.local_entrypoint()
def main(text: str = "Hello from Miso, deployed on Modal."):
    """`modal run modal_app.py` — generate once and save locally as hello.wav."""
    wav = MisoTTS().generate.remote(text=text)
    with open("hello.wav", "wb") as f:
        f.write(wav)
    print(f"Wrote hello.wav ({len(wav):,} bytes)")
