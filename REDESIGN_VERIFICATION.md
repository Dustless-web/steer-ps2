# Carousel and reel redesign — verification

## Open the result

http://127.0.0.1:8765/?run=7d649fd1e389

Run: `7d649fd1e389` — Beyond the weighing scale.

## Implemented

- Five editorial carousel layouts: question, study context, finding, caveat, and invitation.
- Cream/rust palette, serif headlines, abstract line artwork, source footers, and copy fitting.
- Vertical reel with separate animated headline and body layers, phrase captions, narration, progress indicator, and subtitle track.
- Native 1080 × 1920 video rendering at 24 fps. Synthetic narration uses local Flite; phrase timings are approximate, not forced-aligned.
- Gemini structured-output request corrected to responseMimeType/responseJsonSchema.
- Full extracted source supplied to Gemini, followed by a second source-grounded editorial pass. Up to two retries for transient server errors; no automatic quota retries or provider switching.

## Live run

- PDF: resistance-review.pdf, 14 pages, 63,126 extracted characters.
- Gemini model: gemini-3.8-flash; model availability checked with the saved key.
- Live generation and a second live editorial pass completed.
- Exact-quote validation passed for five claims.
- The AI still omitted public-facing context and overstated some null results. A disclosed assistant editorial pass narrowed the sample to one qualified finding. This is not fully unattended clinical-quality generation.
- Original outputs retained as `gemini-initial-draft.json` and `gemini-audited-draft.json` in the run folder.
- Final images and reel rendered through the web-app job flow. Final native-resolution encoding was then rerun locally.
- Carousel contact sheet inspected; reel frame inspected; export remained disabled in the UI.
- HTTP upload, 14-page extraction, source reload, and unapproved release rejection passed.
- 18 unit tests passed, covering integrity, provider handling, and layout fit.
- Video inspected with ffprobe: H.264 1080 × 1920 at 24 fps, AAC audio, mov_text subtitles, approximately 37.6 seconds.
- Manifest hashes verified; live unapproved release correctly rejected. Successful export logic is covered only with synthetic TEST ONLY fixtures, not approval of this medical content.

## Remaining limits

Clinical review is required. Local voice is functional but not a premium neural voice. The visuals are deterministic editorial motion graphics, not generated footage. The current renderer does not integrate Canva or publish to Instagram. No claims have been clinically approved or published.
