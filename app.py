"""Bombas Case Grader: source-aligned PDF/Word grading with teacher final control.

Run: python -m streamlit run app.py
"""
from __future__ import annotations
from datetime import date
import hashlib
import io
from pathlib import Path
import streamlit as st
from rubric_data import ITEMS, MAX_TOTAL, SCORE_GUIDANCE
from rubric_pdf import render_pdf
from grader import extract_submission, assess_with_ai
from rule_grader import segment_student_answers, assess_with_rules

st.set_page_config(page_title='Bombas | Teacher Grading Studio', page_icon='🧦',layout='wide')
st.markdown('''<style>
.block-container{padding-top:1.65rem;max-width:1120px}
.hero{background:linear-gradient(110deg,#16324f,#0d7776);color:white;padding:1.25rem 1.5rem;
 border-radius:12px;margin-bottom:1rem}
.hero h1{color:white;font-size:1.95rem;margin:0 0 .25rem}
.hero p{color:#e5f6f3;margin:0}
[data-testid="stMetric"]{background:#f2f7f8;border:1px solid #d7e5e7;padding:.7rem;border-radius:8px}
</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🧦 Bombas Grading Studio</h1><p>From student submission to a thoughtful, teacher-approved rubric.</p></div>',unsafe_allow_html=True)
st.caption('AP Business with Personal Finance • Topic 1.1 • Teacher-developed 100-point rubric, aligned to the supplied Bombas materials. Not an official College Board assessment.')

BASE=Path(__file__).resolve().parent
with st.sidebar:
    st.header('Rubric & settings')
    st.download_button('Download blank fillable PDF',data=(BASE/'Bombas_Fillable_Rubric.pdf').read_bytes(),
                       file_name='Bombas_Fillable_Rubric.pdf',mime='application/pdf',use_container_width=True)
    st.success('No API key needed for rule-based suggestions or manual grading.')
    tone=st.selectbox('Feedback voice',['Supportive and specific','Concise and professional','Warm coaching with a revision question'])
    with st.expander('Optional OpenAI grading (requires API key)'):
        api_key=st.text_input('OpenAI API key',type='password',help='Optional. AI grading sends extracted student text to OpenAI. Enter only if authorized by your institution.')
        model=st.text_input('Model',value='gpt-4.1-mini',help='Use a model enabled for your API project.')
    st.info('No-API assistance analyzes text inside this running app without sending it to an AI service. Uploaded work is processed in server memory, so check institutional approval and hosting privacy requirements. OpenAI assistance, if selected, transmits extracted student text.')
    st.warning('Every suggestion is a draft, not a final grade. Scanned PDFs, handwriting, and image-only Word content require OCR or manual review.')

st.subheader('1. Add student work')
files=st.file_uploader('Upload one or more student submissions (.docx or .pdf)',
                       type=['docx','pdf'],accept_multiple_files=True,
                       help='If you upload more than one file, select and grade each submission separately.')
options=['✍️ Manual grading (no student document)']
file_map={}
for f in files or []:
    raw=f.getvalue()
    h=hashlib.sha256(raw).hexdigest()[:16]
    label=f'{f.name}  [{h[:6]}]'
    options.append(label)
    file_map[label]=(f.name,raw,h)
selected=st.selectbox('Select submission to assess', options, index=1 if len(options)>1 else 0)
if selected in file_map:
    filename, content, ident=file_map[selected]
    try:
        student_text,warnings=extract_submission(filename,content)
        st.success(f'Loaded {filename} • {len(student_text):,} selectable characters')
        for warning in warnings: st.warning(warning)
        if not student_text.strip(): st.error('No extractable text. Use an OCR-processed file or manual grading.')
        with st.expander('Inspect extracted submission text (verify answers before grading)'):
            st.text_area('Extracted text',value=student_text,height=230,disabled=True)
    except Exception as exc:
        student_text=''
        st.error('Could not read this file: '+str(exc))
else:
    ident='manual';student_text='';filename='Manual rubric'
    st.caption('Use this option for printed assignments or for grading without student uploads.')

prefix='sub_'+ident+'_'
name_hint=Path(filename).stem.replace('_',' ').replace(' (1)','') if ident!='manual' else ''
meta_cols=st.columns([2,2,1])
with meta_cols[0]: student=st.text_input('Student name',value=name_hint,key=prefix+'student')
with meta_cols[1]: teacher=st.text_input('Teacher name',key=prefix+'teacher')
with meta_cols[2]: assessment_date=st.date_input('Date',value=date.today(),key=prefix+'date')

st.subheader('2. Draft scores and feedback')

def load_draft(draft, method):
    for item in draft['grades']:
        st.session_state[prefix+'score_'+item['id']]=str(item['score'])
        st.session_state[prefix+'note_'+item['id']]=item['note'][:115]
        st.session_state[prefix+'evidence_'+item['id']]=item['student_evidence']
    st.session_state[prefix+'response']=draft['teacher_response'][:480]
    st.session_state[prefix+'next']=draft['revision_prompt'][:215]
    st.session_state[prefix+'flags']=draft['review_flags']
    st.session_state[prefix+'method']=method
    st.session_state[prefix+'approved']=False

if ident!='manual':
    parsed, detection_flags = segment_student_answers(student_text)
    # The first upload populates boxes. Teachers may correct PDF/Word extraction
    # and ambiguous numbering before using rule-based suggestions.
    if prefix+'answer_init' not in st.session_state:
        for item in ITEMS:
            st.session_state[prefix+'answer_'+item['id']]=parsed[item['id']]
        st.session_state[prefix+'answer_init']=True
    with st.expander('Review or correct the seven detected answers before grading', expanded=True):
        st.caption('This is especially important for Word/PDF submissions with unusual numbering. '
                   'Edit any incomplete or wrongly matched response; only these answer boxes are used by the no-API grader.')
        for item in ITEMS:
            st.text_area(f"{item['id']} · {item['label']}",key=prefix+'answer_'+item['id'],height=84)
        if detection_flags:
            for warning in detection_flags: st.warning(warning)
    local_answers={i['id']:st.session_state[prefix+'answer_'+i['id']] for i in ITEMS}
    b1,b2=st.columns(2)
    with b1:
        local_button=st.button('🔎 Suggest grades + feedback (NO API)', type='primary',
                               disabled=not any(v.strip() for v in local_answers.values()),
                               use_container_width=True)
    with b2:
        ai_button=st.button('✨ AI-assisted grading (API key)',
                            disabled=not(bool(api_key.strip()) and len(student_text.strip())>=40),
                            use_container_width=True)
    if local_button:
        draft=assess_with_rules(local_answers,tone)
        load_draft(draft,'Rules: no API')
        st.success('Preliminary rule-based suggestions entered. Review each score and comment; the app does not understand nuanced arguments.')
    if ai_button:
        try:
            with st.spinner('Drafting suggestions against the teaching-note criteria…'):
                draft=assess_with_ai(student_text,api_key,model,tone)
            load_draft(draft,'AI draft')
            st.success('AI draft entered. Verify each response, edit scores, and approve the final PDF.')
        except Exception as exc:
            st.error('AI assessment failed: '+str(exc))
    if not api_key.strip():
        st.caption('No API key required: use the left button. AI grading on the right is optional.')
    st.warning('Rule-based grading is a rough draft based on terms and patterns, not reliable semantic evaluation. '
               'It may miss valid paraphrases or over-credit keywords. Review every grade; evaluate the creative application yourself.')

flags=st.session_state.get(prefix+'flags','')
if flags:
    st.warning('Teacher review flags: '+flags)
if st.session_state.get(prefix+'method'):
    st.caption('Current draft source: '+st.session_state[prefix+'method'])

st.caption(SCORE_GUIDANCE)
scores={}; notes={}; problems=[]
for item in ITEMS:
    item_id=item['id']
    with st.container(border=True):
        label_col, score_col=st.columns([4,1])
        with label_col:
            st.markdown(f"**{item_id} · {item['label']}**  —  {item['section']} · {item['max']} points")
            st.caption(item['criterion'])
        with score_col:
            raw_score=st.text_input(f'Points (0–{item["max"]})',key=prefix+'score_'+item_id,placeholder='—',
                                    help='Enter an integer. Leave empty when not yet assessed.')
        if raw_score.strip():
            try:
                number=int(raw_score)
                if number<0 or number>item['max']: raise ValueError()
                scores[item_id]=number
            except ValueError:
                scores[item_id]=None
                problems.append(f'{item_id}: enter a whole number 0–{item["max"]}.')
        else: scores[item_id]=None
        notes[item_id]=st.text_input('Criterion feedback (appears in the rubric row)',key=prefix+'note_'+item_id,
                                      max_chars=115,placeholder='Specific success or point to improve')
        evidence=st.session_state.get(prefix+'evidence_'+item_id,'')
        if evidence: st.caption('Extracted student excerpt (verify against original): '+evidence)

st.subheader('3. Compose teacher response')
response=st.text_area('Personalized teacher response (strength + evidence + next move)',
                      height=130,key=prefix+'response',max_chars=480,
                      placeholder='You recognized the key market gap… To strengthen your explanation…')
next_step=st.text_area('Focused revision question or next step',height=80,
                       key=prefix+'next',max_chars=215,
                       placeholder='What specific testing evidence shows how the product addresses customer needs?')

scored=[v for v in scores.values() if v is not None]
total=sum(scored)
metrics=st.columns(3)
metrics[0].metric('Points entered',f'{total} / {MAX_TOTAL}')
metrics[1].metric('Questions assessed',f'{len(scored)} / {len(ITEMS)}')
metrics[2].metric('Assessment status','Ready for review' if len(scored)==len(ITEMS) and not problems else 'Draft / incomplete')
for issue in problems: st.error(issue)

st.subheader('4. Review & print')
st.caption('The completed PDF is a one-page print-ready copy. The separate blank template is an editable Acrobat form. '
           'The app will export only the grades and comments you review and choose to include.')
approved=st.checkbox('I reviewed the student submission, scores, and written feedback before issuing a final grade.',
                     key=prefix+'approved')
if not all(v is not None for v in scores.values()):
    st.info('You can export a draft with blank scores, or complete all seven score fields first.')
if problems: st.warning('Correct invalid points before exporting.')
try:
    document=render_pdf(student=student,teacher=teacher,marked_date=assessment_date.strftime('%b %d, %Y'),
                        scores=scores,notes=notes,response=response,next_step=next_step,include_fields=False,reviewed=approved)
except Exception as exc:
    document=None
    st.error('PDF rendering error: '+str(exc))
slug=''.join(ch if ch.isalnum() or ch in '-_' else '_' for ch in (student.strip() or 'Student'))[:45]
st.download_button('⬇ Download one-page completed rubric (PDF)',data=document if document else b'',
                   file_name=f'Bombas_Rubric_{slug}.pdf',mime='application/pdf',
                   disabled=bool(problems or not document or not approved),
                   type='primary',use_container_width=True,
                   help='Check the teacher-review box to enable a final PDF. A partially graded draft may be exported after review.')
st.caption('Print tip: Use Actual size / 100% on US Letter paper. The total shows only when all seven question scores have been entered.')
