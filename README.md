# Steer — research to Instagram

A local research-to-content studio for Steer Hackathon PS2, built by **Avinash Sangisetti** with AI assistance. Team partner **Sagarika Patil** worked on PS1; this repository is PS2.

## Submission

- **[Finished posts, source sheet and evidence](submission/README.md)**
- [Workflow and human effort](submission/WORKFLOW.md)
- [Contributors and tools](submission/DISCLOSURE.md)
- [Two-minute walkthrough script](WALKTHROUGH.md) — script only, no recorded Loom.

All outputs are **review drafts**, not clinician-approved medical content. Nothing is published automatically.

## Run locally

Requires Python 3.11+, FFmpeg on PATH and Arial/Georgia (Windows) or DejaVu fonts (Linux).

```sh
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Set `AI_PROVIDER=gemini`, your own `GEMINI_API_KEY`, and a compatible `GEMINI_MODEL` available in your account. Groq and OpenAI are alternative integrations. Provider availability, quotas and charges depend on your account. Keys are excluded from Git.

```sh
python server.py
```

Open **http://127.0.0.1:8765/**. On Windows, `Start Steer.cmd` also launches the server. The app reads `.env` on startup; restart after configuration changes.

## Implemented

- Text-based PDF extraction by page and source fingerprints.
- Structured claims, exact quotations, population, limitations and claim references; Gemini also performs a source-grounded revision pass.
- 1080×1350 carousel PNGs, 1080×1080 static, 1080×1920 animated MP4, SRT, caption and hashtags.
- Paper-specific creative direction: eight story families, four characters and sixteen props from an original illustration library. Edit under **Content → Story & characters**.
- Continuous character animation and locally synthesized sound effects; no narration API required.
- Versioned claim decisions and final-asset review. Edits reset approvals; asset hashes protect releases.
- CLI batches up to five PDFs: `python pipeline.py paper1.pdf paper2.pdf --video local`.

The video is programmatically rendered from AI-assisted copy/direction, not diffusion-generated footage. Unfamiliar topics fall back to generic research illustrations. Existing packs receive transparent local suggestions; new model requests include the creative brief.

## Validation and scope

The submitted resistance pack has saved live Gemini provenance; the nutrition example uses labelled prepared AI-assisted copy. Both were rendered in the playful style. The new creative schema/prompt has **not** had a new live Gemini end-to-end run. No new automated tests were run during the latest integration. Existing tests and old design modules are development history, not proof of current validation.

Quotation matching does not establish medical entailment. Clinician review is still required. No authenticated clinician accounts, automated OCR, Canva integration, scheduling, Hindi localisation, public deployment or recorded Loom is included. The server is local-only, not hardened for public hosting.

See [PLAYFUL_STUDIO.md](PLAYFUL_STUDIO.md) for the renderer.
