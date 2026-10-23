"""Transparent, offline, keyword/concept-based *draft* assessment for Bombas.

No AI, network, API key, trained models, or student data transmission.
The program cannot judge nuanced reasoning, sarcasm, or most paraphrases. All
scores and feedback are preliminary and must be reviewed by the teacher.
"""
from __future__ import annotations

import re
from rubric_data import ITEMS

_IDS = [item['id'] for item in ITEMS]
_HEADERS = {
    'reading': ('R1', 'R2', 'R3'),
    'practice': ('P1', 'P2', 'P3'),
}
# These first-line prompts are removed if the student includes the worksheet
# prompts alongside their answers. The rubric should assess the *answer*, not
# keywords copied from the question.
_PROMPT_STARTS = (
    'what business is featured in this case',
    'what product(s) does the business provide',
    'who is named in the case',
    'and what is/are their role(s)',
    'describe other stakeholders',
    'and groups) with an interest in the business',
    'describe an opportunity and/or challenge',
    'describe the specific customer bombas intended',
    'describe the market opportunity',
    'through their research',
    'explain how heath and goldberg used',
    'explain how the founders used',
    'solution fit',
    'identify one everyday product',
    'improved; for example',
    'reliable.',
)

def has(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text, re.I) for pattern in patterns)


def _remove_prompts(text: str) -> str:
    # Preserve numbered answer bodies, discard standalone question prompts.
    kept = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.lower().startswith('--- pdf page'):
            continue
        if any(s.lower().startswith(start) for start in _PROMPT_STARTS):
            continue
        # Some short worksheet prompts are wrapped onto multiple PDF lines.
        if has(s, r'^\(?city, state, country\)?', r'^and/or challenge facing'):
            continue
        kept.append(s)
    return ' '.join(kept).strip()


def segment_student_answers(student_text: str) -> tuple[dict[str, str], list[str]]:
    """Separate numbered reading/practice questions and application activity.

    Avoid scoring a full submission against every rubric row: if a response
    cannot be assigned to a known question, leave it blank and flag it.
    """
    result = {ident: '' for ident in _IDS}
    issues: list[str] = []
    section: str | None = None
    current: str | None = None
    parts: dict[str, list[str]] = {ident: [] for ident in _IDS}
    numbered_hits = 0

    for line in student_text.replace('\r', '\n').split('\n'):
        line = line.strip()
        if not line or re.match(r'^---\s*PDF page \d+\s*---$', line, re.I):
            continue
        # 'Reading Question 1', 'Practice Q 2', with optional inline answer.
        match = re.match(r'^(reading|practice)\s+(?:question|q)\s*([123])\b[.):\s-]*(.*)$', line, re.I)
        if match:
            section = match.group(1).lower()
            current = _HEADERS[section][int(match.group(2))-1]
            numbered_hits += 1
            if match.group(3).strip():
                parts[current].append(match.group(3).strip())
            continue
        if re.match(r'^reading\s+questions?\s*:?[\s]*$', line, re.I):
            section, current = 'reading', None
            continue
        if re.match(r'^practice\s+questions?\s*:?[\s]*$', line, re.I):
            section, current = 'practice', None
            continue
        match = re.match(r'^(?:application\s+(?:activity|question)|application)\s*[:.]?\s*(.*)$', line, re.I)
        if match:
            current, section = 'A1', 'application'
            numbered_hits += 1
            if match.group(1).strip(): parts[current].append(match.group(1).strip())
            continue
        # Another common style is '1.' beneath Reading Questions / Practice Questions.
        match = re.match(r'^(?:q\s*)?([123])\s*[.)]\s*(.*)$', line, re.I)
        if match and section in _HEADERS:
            current = _HEADERS[section][int(match.group(1))-1]
            numbered_hits += 1
            if match.group(2).strip(): parts[current].append(match.group(2).strip())
            continue
        if current:
            parts[current].append(line)

    for ident in _IDS:
        result[ident] = _remove_prompts('\n'.join(parts[ident]))

    if not numbered_hits:
        issues.append('No recognizable question headings or numbering were found. Paste each answer into its matching box before using assisted grading.')
    missing = [ident for ident in _IDS if not result[ident]]
    if missing:
        issues.append('No student answer was detected for: ' + ', '.join(missing) + '. These will be provisionally scored zero until reviewed.')
    return result, issues


def _grade_one(ident: str, answer: str) -> dict:
    """Concept indicators and short, reviewable rationales; not a semantic grade."""
    t = answer.lower().replace('’', "'")
    if not t.strip():
        return dict(id=ident, score=0, note='No response detected; check the uploaded file.', student_evidence='')
    points = 0
    found: list[str] = []
    missing: list[str] = []
    caution: list[str] = []

    def credit(n: int, ok: bool, found_label: str, missing_label: str) -> None:
        nonlocal points
        if ok:
            points += n
            found.append(found_label)
        else:
            missing.append(missing_label)

    if ident == 'R1':
        credit(4, has(t,r'\bbombas\b'), 'Bombas', 'the business name')
        credit(3, has(t,r'\bsock'), 'socks', 'socks')
        credit(2, has(t,r'comfort',r'high[ -]?quality',r'premium'), 'premium quality', 'quality or comfort')
        credit(1, has(t,r't[ -]?shirts?',r'underwear',r'slides?',r'apparel'), 'expanded products', 'additional product line')
    elif ident == 'R2':
        credit(3, has(t, r'\b(?:david\s+)?heath\b'), 'Heath', 'David Heath')
        credit(3, has(t, r'\b(?:randy\s+)?goldberg\b'), 'Goldberg', 'Randy Goldberg')
        credit(3, has(t, r'found',r'co[ -]?creat',r'started\s+(?:the\s+)?(?:company|business)'), 'founders', 'founders’ role')
        credit(2, has(t, r'customer',r'buyer',r'people\s+who\s+(?:buy|purchase)'), 'customers', 'paying customers')
        credit(2, has(t, r'unhoused',r'homeless',r'people experiencing homelessness',r'donation recipient'), 'donation recipients', 'donation recipients')
        credit(2, has(t, r'crowdfund',r'backer',r'donor',r'investor',r'employee',r'supplier'), 'another stakeholder', 'another stakeholder')
    elif ident == 'R3':
        pricing = has(t, r'pric',r'profit',r'cost',r'expens')
        donation = has(t, r'donat',r'give away',r'free pair',r'\btwo\s+pairs?\b')
        gap = has(t, r'gap',r'lack\s+of',r'need',r'opportunit') and has(t, r'socks?',r'comfort',r'everyday')
        funding = has(t, r'fund',r'crowdfund',r'rais\w+\s+money')
        development = has(t, r'design',r'test',r'product',r'manufactur') and has(t, r'challeng',r'difficult',r'hard')
        if (pricing and donation) or (gap and has(t,r'comfortable',r'quality',r'premium',r'everyday')) or (funding and has(t,r'challenge',r'startup')) or development:
            points=10; found=['supported opportunity/challenge']
        elif pricing or gap or funding or development:
            points=6; found=['relevant opportunity/challenge']; missing=['more case-specific explanation']
        else:
            points=2 if len(t.split())>10 else 0; missing=['supported opportunity or challenge']
    elif ident == 'P1':
        credit(5,has(t,r'pay',r'purchase',r'buy',r'afford',r'disposable\s+income',r'\$\s*1[3-9]',r'\$\s*20'), 'paying power', 'ability/willingness to pay')
        credit(5,has(t,r'donat',r'giv\w+\s+back',r'help\w+\s+others?',r'social\s+(?:good|mission|impact)',r'charit',r'cause'), 'give-back motivation', 'interest in giving back')
        credit(3,has(t,r'millennial',r'younger',r'age\s+group'), 'initial segment', 'specific target segment')
        credit(2,has(t,r'13\s*(?:-|to|–)\s*20',r'\$\s*1[3-9]',r'\$\s*20',r'premium\s+pric'), 'premium price', 'premium price point')
        # The teaching note explicitly distinguishes donated-item recipients from *paying* customers.
        confused = has(t,r'customers?\s+(?:also\s+)?includ\w*\s+(?:the\s+)?(?:unhoused|homeless)',
                       r'customers?\s+(?:are|were)\s+(?:the\s+)?(?:unhoused|homeless)',
                       r'(?:unhoused|homeless)\s+(?:people\s+)?(?:are|were)\s+(?:also\s+)?customers?')
        rejected = has(t,r'not\s+(?:the\s+)?paying\s+customers?',r'recipients?\s+(?:are|were)\s+not\s+customers?')
        if confused and not rejected:
            points=max(0,points-5)
            caution.append('Recipients confused with paying customers')
    elif ident == 'P2':
        credit(5,has(t,r'everyday',r'daily',r'normal\s+wear',r'regular\s+use'), 'everyday use', 'everyday use')
        credit(4,has(t,r'comfort',r'quality',r'premium'), 'quality/comfort', 'high quality or comfort')
        credit(3,has(t,r'cheap',r'inexpens',r'low[ -]?cost',r'basic',r'\$1'), 'cheap basics', 'basic sock comparison')
        credit(3,has(t,r'sport',r'athlet',r'perform',r'running',r'hiking'), 'sport socks', 'sport/performance sock comparison')
    elif ident == 'P3':
        credit(5,has(t,r'market\s+research.{0,100}(?:need|gap|problem|customer|opportunit)',r'gap',r'unmet\s+need',r'customers?\s+(?:need|want)',r'lack\s+of',r'demand'), 'market need', 'research identifying unmet need')
        credit(5,has(t,r'tried\s+(?:different\s+)?socks',r'technic',r'featur',r'material',r'fabric',r'arch\s+support',r'seam',r'wool',r'comfort'), 'technical features', 'technical/design research')
        credit(4,has(t,r'expert',r'manufactur',r'fashion',r'designer'), 'industry expertise', 'consulting manufacturing/fashion experts')
        credit(4,has(t,r'feedbac',r'test',r'trial',r'prototyp',r'iterat'), 'customer testing', 'customer feedback/testing')
        credit(2,has(t,r'improv',r'fit',r'solv',r'address\w+\s+the\s+(?:problem|need)',r'meet\w*\s+(?:their|customer)\s+need'), 'connection to fit', 'explain the problem–solution link')
    elif ident == 'A1':
        # Open-ended creative prompts cannot be reliably assessed by keywords.
        # These are deliberately *conservative* draft points to inspect, not an answer key.
        words=len(t.split())
        points = 0 if words<5 else 6 if words<14 else 10 if words<25 else 12
        found=['substantive application attempt'] if points else []
        caution.append('Creative product proposal requires teacher judgment')
        missing=['verify product, improvement and benefit manually']
    else:
        raise ValueError(f'Unknown item ID: {ident}')

    max_points=next(item['max'] for item in ITEMS if item['id']==ident)
    points=min(max_points,points)
    note = ('Check: '+ '; '.join(caution[:1])+'.') if caution else ''
    if missing:
        note = (note+' Revisit: '+', '.join(missing[:2])+'.').strip()
    elif found:
        note = ('Found: '+', '.join(found[:3])+'.')
    # Row comments are short enough for the 3-line printed PDF column.
    if ident=='P1' and caution:
        note='Donation recipients are not paying buyers; clarify target.'
    elif ident=='A1':
        note='Teacher review: product, improvement, and user benefit.'
    elif ident=='P3' and 'research identifying unmet need' in missing:
        note='Explain how market research identified the unmet need.'
    elif ident=='R2' and 'another stakeholder' in missing:
        note='Add another stakeholder (e.g., crowdfunding backers).'
    elif len(note)>64:
        note=note[:61].rsplit(' ',1)[0]+'...'
    return dict(id=ident,score=points,note=note,student_evidence=answer[:130])


def assess_with_rules(answers: dict[str,str], tone: str='Supportive and specific') -> dict:
    """Return the same draft schema as assess_with_ai, but with zero network use."""
    grades=[_grade_one(item['id'], answers.get(item['id'],'') or '') for item in ITEMS]
    labels={i['id']:i['label'].lower() for i in ITEMS}
    all_blank=all(not answers.get(i,'').strip() for i in _IDS)
    if all_blank:
        teacher_response='No student answers were detected. Please verify the document extraction or manually enter each response before grading.'
        next_step='Provide responses to the seven case questions, then resubmit for review.'
    else:
        # Prefer specific case-analysis achievements over mere fact recall if
        # coverage rates tie. We do not quote/evaluate unsupported reasoning.
        priority={'P2':7,'R3':6,'P3':5,'R2':4,'R1':3,'P1':2,'A1':1}
        strongest=max(grades,key=lambda x:(x['score']/next(i['max'] for i in ITEMS if i['id']==x['id']),priority[x['id']]))
        weakest=min(grades,key=lambda x:(x['score']/next(i['max'] for i in ITEMS if i['id']==x['id']),-priority[x['id']]))
        strengths={
            'R1':'You identified Bombas and its products.',
            'R2':'You identified the founders and stakeholders involved in Bombas.',
            'R3':'You identified a real business opportunity or challenge, such as pricing or product development.',
            'P1':'You described the market Bombas wanted to reach.',
            'P2':'You distinguished the need for premium everyday socks from the existing basic and sport-sock options.',
            'P3':'You connected product research and testing to the development of Bombas socks.',
            'A1':'You attempted to apply product-improvement thinking to an everyday object.',
        }
        next_steps={
            'R1': ('Add the main product line and explain how the business expanded its offerings.',
                   'What does Bombas sell in addition to its original premium socks?'),
            'R2': ('Name both founders and describe other stakeholders, including customers and donation recipients.',
                   'Who founded Bombas, and which other groups had an interest in the company?'),
            'R3': ('Explain one challenge or opportunity with a precise supporting detail from the case.',
                   'How did Bombas balance product price, donation costs, and profitability?'),
            'P1': ('Distinguish paying buyers from the people who receive donated socks. Discuss why buyers accept a premium price.',
                   'Who pays $13–$20 for Bombas socks, and how is that group different from donation recipients?'),
            'P2': ('Explain the contrast between low-cost basics, athletic socks, and unmet everyday comfort needs.',
                   'What was missing between inexpensive daily socks and specialized sport socks?'),
            'P3': ('Explain what the founders learned about customer demand, not only how they tested sock features.',
                   'What did market research reveal before the founders refined the sock design?'),
            'A1': ('Clarify the proposed product change and the specific user benefit. Evaluate feasibility with the teacher.',
                   'What need would your proposed improvement address, and how could you test it?'),
        }
        improve, next_step=next_steps[weakest['id']]
        teacher_response=(strengths[strongest['id']]+' '+improve+
                          ' This is rule-based feedback; I will check your reasoning before finalizing the rubric.')
        if tone=='Concise and professional':
            teacher_response=(strengths[strongest['id']]+' '+improve+' Teacher review required.')
        elif tone=='Warm coaching with a revision question':
            teacher_response=(strengths[strongest['id']]+' '+improve+
                              ' Revisit the case and use evidence to make the connection clearer.')
    flags=('RULE-BASED DRAFT ONLY: Matches words and simple patterns, not nuanced reasoning. '
           'Verify evidence, negation, synonyms, interpretations, and all scores. '
           'The open-ended application task (A1) needs manual evaluation. '
           'No student content was transmitted to an AI service.')
    if any(not answers.get(i,'').strip() for i in _IDS):
        flags+=' Some answers are blank or could not be detected; verify segmentation.'
    if has(answers.get('P1',''),r'customers?\s+(?:also\s+)?includ\w*\s+(?:the\s+)?(?:unhoused|homeless)'):
        flags+=' P1 may confuse paying customers with donated-item recipients.'
    return dict(grades=grades,teacher_response=teacher_response[:480],
                revision_prompt=next_step[:215],review_flags=flags)
