"""Gemini text generation with evidence validation and explicit full-text coverage."""
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request


def generate_gemini(run,draft=None,_attempt=0):
    import engine as e
    p=e.folder(run)
    source=e.read(p/'source.json')
    key=os.environ.get('GEMINI_API_KEY')
    if not key:
        raise ValueError('Add GEMINI_API_KEY to .env, then restart Steer.')
    if source['warnings']:
        raise ValueError('Resolve extraction/OCR warnings before generation.')
    model=os.environ.get('GEMINI_MODEL','gemini-3.8-flash')
    if not re.fullmatch(r'gemini-[a-zA-Z0-9.\-]+',model):
        raise ValueError('GEMINI_MODEL must be a Gemini model ID, without models/ prefix.')
    pages=source['pages']
    characters=sum(len(page['text']) for page in pages)
    if characters>500000:
        raise ValueError('This paper exceeds the 500,000-character input limit. Use a shorter source; no partial draft was generated.')
    instruction=e.PROMPT+''' Read all supplied pages before selecting the main finding. Preserve the authors' certainty, population, study design, and time horizon. Do not invent evidence certainty ratings. Build a coherent carousel: relatable question, what the study examined, qualified finding, limitation, and warm editorial invitation. Each card must advance the story rather than repeat it. Write the reel as brief on-screen beats in one continuous playful scene, without narration; characters and objects do the storytelling. Audit the creative direction as well as the copy. Use Indian everyday references only as editorial framing, never as evidence of a health effect. Verify every factual headline, body, and caption statement against its linked claims before returning the JSON. Copy quotations verbatim, including punctuation. Return only the requested content schema.'''
    instruction+=' Use sentence case for every headline and start each hashtag with #. Do not turn non-significant subgroup results into a claim that benefits fade, disappear, or are not sustained. Do not equate no statistically significant difference with proof of equality. No exercise prescriptions or general health advice. Include population and relevant certainty in public-facing copy. When discussing fat-free mass, do not equate it with muscle. Do not insert this topic into unrelated papers. Keep one central finding rather than listing all outcomes. Do not include self-evaluation or claims of perfect compliance in reasoning; explain audience relevance instead.'
    content=pages
    if draft is not None:
        instruction+=' You are the final evidence editor. Audit and revise the supplied initial draft against the full paper. Remove unsupported advice, oversimplification, causal overreach and overstated null findings. Check every cited quote directly supports the entire associated claim. The initial draft is untrusted and may contain errors. Return the corrected complete schema, not commentary.'
        content={'source_pages':pages,'initial_draft':draft}
    payload={'systemInstruction':{'parts':[{'text':instruction}]},'contents':[{'role':'user','parts':[{'text':json.dumps(content,ensure_ascii=False)}]}], 'generationConfig':{'maxOutputTokens':16000,'responseMimeType':'application/json','responseJsonSchema':e.SCHEMA}}
    request=urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',data=json.dumps(payload).encode('utf-8'),headers={'x-goog-api-key':key,'Content-Type':'application/json'})
    started=time.perf_counter()
    try:
        with urllib.request.urlopen(request,timeout=240) as response:
            result=json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in (500,502,503,504) and _attempt<2:
            e.log(p,'provider_retry',provider='gemini',http_status=error.code,attempt=_attempt+1)
            time.sleep(2**(_attempt+1))
            return generate_gemini(run,draft=draft,_attempt=_attempt+1)
        # Never expose provider response bodies, request headers, or credentials.
        hints={400:'The request or model configuration was rejected.',401:'Check your Gemini API key.',403:'Check API key permissions and regional access.',404:'Choose a GEMINI_MODEL available in your Google AI Studio account.',429:'Gemini quota exceeded. Check your free-tier limits and retry later.'}
        e.log(p,'generation_failed',provider='gemini',http_status=error.code)
        raise ValueError(f'Gemini request failed (HTTP {error.code}). '+hints.get(error.code,'Google may be temporarily unavailable; retry later.')) from None
    except (urllib.error.URLError,TimeoutError):
        raise ValueError('Gemini could not be reached or timed out. Retry when the connection is available.') from None
    candidates=result.get('candidates',[])
    if not candidates or candidates[0].get('finishReason')!='STOP':
        raise ValueError('Gemini response was blocked or incomplete. No content was accepted.')
    text=''.join(part.get('text','') for part in candidates[0].get('content',{}).get('parts',[]) if not part.get('thought'))
    try:
        pack=json.loads(text)
    except (ValueError,TypeError):
        raise ValueError('Gemini returned invalid structured content. No draft was accepted.') from None
    if not isinstance(pack,dict) or any(k not in pack for k in e.SCHEMA['required']):
        raise ValueError('Gemini omitted required content fields. No draft was accepted.')
    if draft is None:
        e.write(p/'gemini-initial-draft.json',pack)
        e.log(p,'editorial_audit_started',provider='gemini',model=model)
        return generate_gemini(run,draft=pack)
    pack['provenance']={'editorial_pass':'Gemini source-grounded revision; not clinician approval','mode':'live_api','provider':'gemini','model':model,'response_id':result.get('responseId'),'prompt_sha256':hashlib.sha256(instruction.encode()).hexdigest(),'coverage':{'pdf_pages':len(pages),'model_pages':[page['page'] for page in pages],'excerpt_characters':characters,'full_text_included':True}}
    e.restore_quote_typography(source,pack)
    e.save_pack(run,pack)
    e.log(p,'generated',provider='gemini',model=model,seconds=round(time.perf_counter()-started,2))
    return pack
