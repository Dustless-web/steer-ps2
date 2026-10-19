# Runbook

See [README.md](README.md) for setup and current capability, [PLAYFUL_STUDIO.md](PLAYFUL_STUDIO.md) for rendering and [submission/WORKFLOW.md](submission/WORKFLOW.md) for effort/validation.

1. Install Python requirements and FFmpeg.
2. Copy `.env.example` to `.env` and configure your key/provider/model.
3. Run `python server.py` or `Start Steer.cmd` on Windows.
4. Upload a PDF at http://127.0.0.1:8765/ and generate copy.
5. Inspect claims and direction; build images/reel.
6. A clinician reviews claims, caption, visuals and limitations.
7. Export only after current-version approval. Nothing is posted automatically.

Local credentials, runs, logs and PDFs are excluded from Git. Read-only examples are under `submission/`. Use `--video local` for batch animation; legacy neural flags are not supported by the playful renderer.
