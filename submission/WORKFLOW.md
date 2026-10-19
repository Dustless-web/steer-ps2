# Pipeline and human effort

```mermaid
flowchart LR
 A[Upload PDF] --> B[Extract pages and fingerprint]
 B --> C[AI copy and creative brief]
 C --> D[Source revision and quote validation]
 D --> E[PNG and animated MP4]
 E --> F[Doctor reviews claims and final assets]
 F --> G[Version and hash gated export]
```

`server.py` provides the API, background jobs and browser UI. `engine.py` retains source pages, validates references/quotes and manages reviews. `gemini_provider.py` performs generation plus source-grounded editing. Prompts are in these files and `creative.py`. `playful_art.py` draws original objects; `playful.py` renders with Pillow/FFmpeg. `pipeline.py` batches up to five PDFs.

Story families: comparison, association, timeline, mechanism, review, methods, qualitative and uncertainty. The model selects a supported character/props from paper context and cites motivating claim IDs. Saved packs use labelled local inference. Visual implications still require review.

## Active human time — estimates, not measured results

| Step | Estimate |
| --- | --- |
| Select and upload paper | 1–3 min |
| Inspect extraction and scope | 2–5 min |
| Clinician checks claims/context | 5–15 min |
| Review visuals/caption and edit | 3–7 min |
| Final review/export | 1–2 min |
| **Total** | **12–32 min per paper** |

Model/renderer waiting is excluded. The latest local full-resolution reel took several minutes; CPU and copy length affect speed. Static text caching was added for subsequent exports. Difficult papers or revisions take longer. No clinician timing study has been performed.

The submitted resistance pack has saved live Gemini provenance; nutrition copy is prepared. The latest exports exist here. The newest creative schema has not been live-tested with Gemini. A walkthrough script is included, not a recording. No public deployment or automatic publishing is claimed.
