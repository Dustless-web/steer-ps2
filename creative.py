"""Constrained creative direction: paper-specific choices, never scientific evidence."""
import re
STORIES=['comparison','association','timeline','mechanism','review','methods','qualitative','uncertainty']
CHARACTERS=['paper','magnifier','robot','leaf']
PROPS=['book','scale','plate','band','clock','heart','cell','leaf','water','chip','flask','brain','network','thermometer','cloud','question']
SCHEMA={'type':'object','additionalProperties':False,'properties':{
 'story_type':{'type':'string','enum':STORIES},'character':{'type':'string','enum':CHARACTERS},
 'hero_prop':{'type':'string','enum':PROPS},'supporting_props':{'type':'array','items':{'type':'string','enum':PROPS},'minItems':1,'maxItems':2},
 'rationale':{'type':'string'},'evidence_ids':{'type':'array','items':{'type':'string'},'minItems':1}},
 'required':['story_type','character','hero_prop','supporting_props','rationale','evidence_ids']}
INSTRUCTION='''Choose the creative object from the actual paper, not a reusable weight-loss example. Set creative.story_type from the study design: review for evidence synthesis; comparison for a controlled comparison; association for correlations; timeline for longitudinal or before-after observations; mechanism for a proposed mechanism or simulation; methods for a tool, algorithm or theory; qualitative for themes/interviews; uncertainty for inconclusive evidence. An animation is conceptual, never a simulated treatment outcome. Choose a relevant character and props only from the supplied catalog. Use book/question if no specific prop fits. Cite the claim IDs that motivate the direction in creative.evidence_ids and explain why in creative.rationale. Do not depict weight loss, body changes, numerical effect sizes, clinical endorsements, invented quotations or causal arrows. Write a playful visual story with a concrete hook, an investigation, one finding and an honest boundary. Use short sentence-case headlines (prefer <=45 characters) and brief on-screen text (prefer <=120 characters), not narration. No logo introduction, generic motivational advice or paragraphs of speech. Keep necessary population, certainty and limitations visible in the sequence. Different papers must have genuinely different creative choices. All scientific content belongs in evidence-linked blocks, never in prop labels.'''

def validate(plan,ids):
 errors=[]
 if not isinstance(plan,dict):return ['Creative direction must be an object']
 for key,choices in [('story_type',STORIES),('character',CHARACTERS),('hero_prop',PROPS)]:
  if plan.get(key) not in choices:errors.append('Unsupported creative '+key)
 props=plan.get('supporting_props')
 if not isinstance(props,list) or not 1<=len(props)<=2 or any(p not in PROPS for p in props):errors.append('Choose one or two supported props')
 refs=plan.get('evidence_ids')
 if not isinstance(refs,list) or not refs or not set(refs)<=ids:errors.append('Creative direction must reference existing evidence claims')
 if not isinstance(plan.get('rationale'),str) or not plan['rationale'].strip() or len(plan['rationale'])>1500:errors.append('Explain the creative direction in at most 1500 characters')
 return errors

def infer(pack):
 """Transparent no-API fallback for previously saved packs. No copy is changed."""
 design=pack.get('study_design','').lower()
 if re.search(r'meta.?analysis|systematic|review',design):story='review'
 elif re.search(r'qualitative|interview|ethnograph|focus group',design):story='qualitative'
 elif re.search(r'before(?:.and)?.after|pre.?post|longitudinal|follow.up',design):story='timeline'
 elif re.search(r'observational|cohort|cross.section|correlat|association|case.control',design):story='association'
 elif re.search(r'random|controlled|trial|experiment',design):story='comparison'
 elif re.search(r'simulation|mechanis|model',design):story='mechanism'
 elif re.search(r'algorithm|method|proof|theor|benchmark',design):story='methods'
 else:story='uncertainty'
 text=' '.join([pack.get('title','')]*3+[pack.get('message',''),pack.get('study_design','')]+[c.get('text','') for c in pack.get('claims',[])]).lower()
 rules=[('chip',r'algorithm|comput|machine learning|neural network|semiconductor'),('leaf',r'plant|crop|soil|forest|seed|photosynth'),('cloud',r'climate|atmospher|rainfall|carbon emission'),('water',r'water|ocean|marine|hydrolog'),('brain',r'cogniti|memory|brain|sleep|mental'),('heart',r'cardiac|cardiovascular|blood pressure|heart'),('cell',r'cell|gene|protein|insulin|glucose'),('band',r'resistance|strength|exercise'),('plate',r'nutrition|diet|food|meal'),('scale',r'weight|obesity|body mass'),('thermometer',r'temperatur|heat|fever'),('flask',r'chemical|cataly|compound|laboratory')]
 scored=sorted([(len(re.findall(pattern,text)),i,prop) for i,(prop,pattern) in enumerate(rules)],key=lambda x:(-x[0],x[1]))
 chosen=[p for score,_,p in scored if score][:3] or ['book']
 hero=chosen[0];supports=chosen[1:3] or (['clock'] if story=='timeline' else ['question'] if hero=='book' else ['book'])
 char='robot' if hero=='chip' else 'leaf' if hero in ['leaf','water','cloud'] else 'magnifier' if story in ['association','qualitative','uncertainty'] else 'paper'
 return dict(story_type=story,character=char,hero_prop=hero,supporting_props=supports,rationale=f'Inferred from saved study design ({pack.get("study_design","unspecified")}) and evidence topic. {story.capitalize()} motion with {hero} as the subject and {char} as investigator. Review or change these choices before rendering.',evidence_ids=[c['id'] for c in pack.get('claims',[])][:3])

def ensure(run):
 import engine as e
 p=e.folder(run);pack=e.read(p/'pack.json')
 if 'creative' not in pack:
  pack['creative']=infer(pack)
  pack.setdefault('provenance',{})['creative_selection']='Inferred locally from saved evidence; no model call'
  e.save_pack(run,pack)
 return pack
