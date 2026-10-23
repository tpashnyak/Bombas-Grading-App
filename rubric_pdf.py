"""Create an original interactive one-page PDF rubric and print-ready completed copies."""
from __future__ import annotations
from io import BytesIO
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import simpleSplit
from rubric_data import ITEMS, MAX_TOTAL, SCORE_GUIDANCE

WIDTH, HEIGHT = 612, 792
NAVY = HexColor('#16324F')
TEAL = HexColor('#0D7776')
MID = HexColor('#516376')
LIGHT = HexColor('#EAF2F4')
BORDER = HexColor('#BECAD2')
PALE = HexColor('#F6F9FB')
TEXT = HexColor('#213247')


def _text(c, x, y, s, size=9, color=TEXT, font='Helvetica'):
    c.setFillColor(color); c.setFont(font, size); c.drawString(x, y, str(s))


def _fit(c, x, y, s, width, max_size=9, min_size=6.8, color=TEXT, font='Helvetica'):
    size=max_size
    while stringWidth(str(s), font, size)>width and size>min_size:
        size-=.2
    _text(c,x,y,str(s),size,color,font)


def _lines(c, x, top, text, width, size=8, line_height=10, max_lines=3, color=TEXT):
    c.setFont('Helvetica', size); c.setFillColor(color)
    lines = []
    for raw in str(text or '').splitlines():
        if not raw:
            lines.append('')
        else:
            lines.extend(simpleSplit(raw,'Helvetica',size,width))
    for idx, line in enumerate(lines[:max_lines]):
        if idx == max_lines-1 and len(lines)>max_lines:
            line=line.rstrip(' .')+'...'
        c.drawString(x,top-idx*line_height,line)


def _form(c, name, x,y,w,h, value='', multiline=False, font_size=9, tooltip=None):
    kw=dict(name=name,tooltip=tooltip or name,x=x,y=y,width=w,height=h,
            borderStyle='solid',borderWidth=.7,borderColor=BORDER,fillColor=white,
            textColor=TEXT,forceBorder=True,fontName='Helvetica',fontSize=font_size,
            value=str(value or ''))
    if multiline:
        kw['fieldFlags']='multiline'
    c.acroForm.textfield(**kw)


def _static_box(c, x,y,w,h, value='', font=9, max_lines=2):
    c.setStrokeColor(BORDER); c.setLineWidth(.7); c.setFillColor(white)
    c.roundRect(x,y,w,h,3,fill=1,stroke=1)
    _lines(c,x+5,y+h-11,value,w-10,font,font+1.5,max_lines)


def render_pdf(student='', teacher='', marked_date='', scores=None, notes=None,
               response='', next_step='', include_fields=True, reviewed=False):
    """Return PDF bytes. Blank version is an AcroForm; populated version print-ready."""
    scores = scores or {}; notes = notes or {}
    out=BytesIO()
    c=canvas.Canvas(out,pagesize=(WIDTH,HEIGHT),pageCompression=1)
    c.setTitle('Bombas Case Analysis | Teacher-Created 100-Point Rubric')
    c.setAuthor('Teacher-created instructional rubric')
    # Header
    c.setFillColor(NAVY); c.rect(0,708,WIDTH,84,fill=1,stroke=0)
    _text(c,34,756,'BOMBAS  /  CASE ANALYSIS RUBRIC',18,white,'Helvetica-Bold')
    _text(c,35,734,'AP Business with Personal Finance  |  Topic 1.1: What Is a Business?',9.7,white)
    _text(c,35,719,'Teacher-created assessment  •  Reading, practice, and application',8,HexColor('#CADBE5'))
    _text(c,34,690,'STUDENT',7.3,MID,'Helvetica-Bold')
    _text(c,294,690,'TEACHER',7.3,MID,'Helvetica-Bold')
    _text(c,479,690,'DATE',7.3,MID,'Helvetica-Bold')
    metadata=[('student',student,34,661,249),('teacher',teacher,294,661,174),('date',marked_date,479,661,99)]
    for name,val,x,y,w in metadata:
        if include_fields: _form(c,name,x,y,w,24,val,9)
        else: _static_box(c,x,y,w,24,val,9)
    c.setFillColor(LIGHT); c.roundRect(34,634,544,20,4,fill=1,stroke=0)
    _text(c,42,640,'SCORING  |  Award partial credit for accurate evidence; accept equivalent wording. Teacher reviews all scores.',8,TEAL)
    # Table headings
    xs=[34,68,357,409,462,578]
    c.setFillColor(NAVY); c.rect(34,604,544,26,fill=1,stroke=0)
    for x,t in [(43,'ITEM'),(76,'EVIDENCE TO LOOK FOR'),(365,'MAX'),(417,'EARNED'),(470,'QUICK NOTE')]:
        _text(c,x,614,t,7.6,white,'Helvetica-Bold')
    for idx,item in enumerate(ITEMS):
        y=604-(idx+1)*48
        c.setFillColor(PALE if idx%2==0 else white); c.rect(34,y,544,48,fill=1,stroke=0)
        c.setStrokeColor(BORDER); c.setLineWidth(.5); c.line(34,y,578,y)
        for split in xs[1:-1]: c.line(split,y,split,y+48)
        _text(c,40,y+25,item['id'],10,NAVY,'Helvetica-Bold')
        _text(c,75,y+33,item['label'].upper(),7.8,NAVY,'Helvetica-Bold')
        _lines(c,75,y+21,item['criterion'],275,7.65,9.8,2,TEXT)
        _text(c,372,y+20,str(item['max']),10,TEAL,'Helvetica-Bold')
        sc=scores.get(item['id'],None)
        sc_txt='' if sc is None else str(sc)
        note=notes.get(item['id'],'') or ''
        if include_fields:
            _form(c,'score_'+item['id'],416,y+10,39,27,sc_txt,10,
                  tooltip=f"Points earned for {item['id']} (0-{item['max']})")
            _form(c,'note_'+item['id'],469,y+7,102,34,note,True,7.6,
                  tooltip=f"Brief feedback for {item['id']}")
        else:
            _static_box(c,416,y+10,39,27,sc_txt,10,1)
            _static_box(c,469,y+7,102,34,note,7,3)
    # Bottom of table y=268
    c.setStrokeColor(BORDER); c.line(34,268,578,268)
    c.setFillColor(LIGHT); c.roundRect(34,230,544,30,4,fill=1,stroke=0)
    _text(c,44,240,'TOTAL SCORE',10,NAVY,'Helvetica-Bold')
    _text(c,186,240,'/ 100 points',9,MID)
    score_values=[scores.get(i['id']) for i in ITEMS]
    total = sum(float(v) for v in score_values if v is not None and v!='')
    shown_total = (str(int(total)) if total == int(total) else str(round(total,1))) if all(v is not None and v!='' for v in score_values) else ''
    if include_fields: _form(c,'total_score',131,234,47,23,shown_total,10)
    else: _static_box(c,131,234,47,23,shown_total,10,1)
    _text(c,332,240,('STATUS  |  Teacher reviewed' if reviewed else 'STATUS  |  Teacher review required'),8.3,TEAL,'Helvetica-Bold')
    _text(c,34,212,'TEACHER RESPONSE  /  STRENGTHS + EVIDENCE-BASED FEEDBACK',8.2,NAVY,'Helvetica-Bold')
    if include_fields: _form(c,'teacher_response',34,118,544,88,response,True,9,'Teacher response (multiline)')
    else: _static_box(c,34,118,544,88,response,9,7)
    _text(c,34,103,'NEXT STEP  /  REVISION PROMPT',8.2,NAVY,'Helvetica-Bold')
    if include_fields: _form(c,'next_step',34,49,544,47,next_step,True,9,'Revision guidance (multiline)')
    else: _static_box(c,34,49,544,47,next_step,8.5,4)
    _text(c,34,32,'Scoring guide: full = accurate + complete; partial = some correct evidence; zero = absent / off-topic.',7,MID)
    _text(c,34,20,'Not an official College Board rubric. Record a final grade only after human review.',7,MID)
    c.showPage(); c.save()
    return out.getvalue()

if __name__=='__main__':
    from pathlib import Path
    Path(__file__).with_name('Bombas_Fillable_Rubric.pdf').write_bytes(render_pdf())
    print('Wrote PDF template')
