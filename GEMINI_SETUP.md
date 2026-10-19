# Gemini setup

In the local .env file, set:

    AI_PROVIDER=gemini
    GEMINI_API_KEY=your_key_here
    GEMINI_MODEL=gemini-3.8-flash

Never paste the actual key into chat or commit .env. Restart the local server after changing settings. The chosen model must be available to your Google AI Studio project; free-tier quotas and eligibility depend on the model and account. No automatic provider fallback or billing enablement is performed.

Gemini receives all extracted pages (up to 500,000 characters), with PDF page numbers. Larger sources are rejected rather than silently truncated. Output passes the existing exact quotation and structural validation before saving. Clinical approval remains required.

This integration changes research-to-copy generation. Existing image layouts and video rendering are unchanged. Live full-paper generation has been verified. A second source-grounded editorial pass revises the draft before it is accepted. Exact-quote checks do not replace clinical review. Temporary 5xx errors retry at most twice; quota errors do not retry automatically.

API reference: https://ai.google.dev/gemini-api/docs/generate-content/structured-output
