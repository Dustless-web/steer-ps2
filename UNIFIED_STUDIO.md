# Unified studio

Open http://127.0.0.1:8765 after starting `Start Steer.cmd`.
The root page is the single supported interface. Legacy index.html and engine.html URLs redirect to it.

1. Add a research PDF to the searchable paper library.
2. Review extraction, then create a content pack. This runs provider generation and local image/video rendering in a background job.
3. Read the source-linked evidence. Edit slide copy, captions, hashtags, and claim references under Content. Save and rebuild assets after changes.
4. A clinician records decisions for every claim and reviews the current final assets. Save the review before exporting the evidence-linked review package.

Jobs reconnect after browser refresh. A server restart marks an interrupted job as failed, with saved copy retained for recovery. Generation is serialized to prevent conflicting writes. Groq quotas and source validation can still stop generation; the interface reports the failure without marking the job complete.

Local narration depends on FFmpeg's Flite support. Without it, the renderer creates a silent reel and the interface discloses this. These are motion-graphic reels, not generative video footage. This local app does not authenticate clinical credentials or publish to Instagram. Export retains review draft labels.

Implementation: index.html, app.css, app.js, server.py. Older prototype scripts are no longer served.
