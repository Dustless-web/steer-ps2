# Groq setup

The selected provider is Groq. Add your key to the `GROQ_API_KEY=` line in the local `.env` file. Do not put it in `.env.example` or chat.

```dotenv
AI_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

The model is hosted by Groq; its name does not mean requests use OpenAI credits. Requests go only to `https://api.groq.com/openai/v1/chat/completions`. There is no automatic paid-provider fallback. Keep your Groq account on its free plan if you want no API charges; quotas still apply. See [Groq billing](https://console.groq.com/docs/billing-faqs) and [structured outputs](https://console.groq.com/docs/structured-outputs).

Restart the server after editing `.env`. The working app displays the selected provider and whether its key is present; key presence does not verify account quota or successful authentication.

Upload a PDF, generate with AI, render PNGs, and select **Render narrated reel** for local synthetic speech. The neural OpenAI option is disabled for the Groq route. Review decisions still gate release. Live Groq generation was verified on 18 October 2026. Run ed360b344a39 contains generated claims, PNGs and a 33-second local-voice reel. The model saw 9000 characters from PDF pages 1–2 to fit request limits. An editorial pass corrected unsupported advice and overstatements; the original rejected response is retained. Clinical approval remains pending.
