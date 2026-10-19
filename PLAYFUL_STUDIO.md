# Playful content studio

The default renderer is playful-v1: original illustrated characters, a continuous animated set, short on-screen copy and synthesized sound effects. No voice API is used.

## Paper-specific direction
New AI generations include a structured creative brief in the existing generation request: study-design story family, investigator character, main prop, one or two supporting props, rationale, and evidence IDs. The renderer supports eight story families and a constrained illustration catalog. It does not generate arbitrary cinematic footage.

Previously saved packs receive a local suggestion from study design and evidence topics when rendered. Existing copy is preserved. Unknown subjects use a book/question fallback. Content > Story & characters allows overrides. Saving direction invalidates approvals; rebuild and review the resulting assets.

## Files
- creative.py: schema, model instructions, legacy-pack inference and validation
- playful_art.py: reusable original artwork
- playful.py: carousel/static composition and continuous MP4 animation
- engine.py and gemini_provider.py: structured generation, evidence validation and rendering
- app.js: editable creative direction and previews

Creative evidence IDs explain the direction; they do not validate a metaphor scientifically. Doctor review must check both claims and visual implications. Association scenes have no causal arrows; illustrations do not show invented numeric outcomes.

Actual saved resistance-review and nutrition-intervention packs were rendered during integration. No new live Gemini generation or automated test suite was run for this change. Existing longer copy stays longer until edited or regenerated with the new prompt.
