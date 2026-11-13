"""Build the current report from maintained Markdown, with genuine UI captures if present."""
from html import escape
from pathlib import Path
import re
import shutil

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle

ROOT=Path(__file__).resolve().parents[1]
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportBody',fontName='Helvetica',fontSize=9.5,leading=13,spaceAfter=6))
styles.add(ParagraphStyle(name='Cell',fontName='Helvetica',fontSize=8,leading=11,spaceAfter=0))
styles.add(ParagraphStyle(name='CodeLine',fontName='Courier',fontSize=7,leading=10,spaceAfter=2,wordWrap='CJK'))
styles.add(ParagraphStyle(name='CompactBody',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=5))
for name in ['Title','Heading1','Heading2','Heading3']:
    styles[name].textColor=colors.HexColor('#153c34')
    styles[name].keepWithNext=True
styles['Title'].fontSize=27
styles['Title'].leading=32
story=[]


def inline(text):
    text=escape(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)
    text=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',text)
    return text


def add_markdown(path):
    lines=path.read_text(encoding='utf-8').splitlines()
    body=styles['CompactBody' if path.name=='DEMO_GUIDE.md' else 'ReportBody']
    i=0
    code=False
    while i<len(lines):
        line=lines[i]
        if line.startswith('```'):
            code=not code
        elif not line.strip():
            # Paragraph spacing handles separation without orphaning a heading
            # by attaching its keepWithNext rule to a standalone spacer.
            pass
        elif code:
            story.append(Paragraph(escape(line),styles['CodeLine']))
        elif line.startswith('|'):
            data=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[v.strip() for v in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',v) for v in cells):
                    data.append([Paragraph(inline(v),styles['Cell']) for v in cells])
                i+=1
            width=A4[0]-88
            cols=len(data[0])
            fractions={3:[.22,.52,.26],4:[.18,.20,.31,.31],2:[.72,.28]}.get(cols,[1/cols]*cols)
            t=Table(data,colWidths=[width*f for f in fractions],repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3eddf')),
                ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#d3dbd0')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),
                ('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),7),
                ('RIGHTPADDING',(0,0),(-1,-1),7)]))
            story.append(t)
            story.append(Spacer(1,12))
            continue
        elif line.startswith('# '):
            story.append(Paragraph(inline(line[2:]),styles['Title']))
        elif line.startswith('## '):
            story.append(Paragraph(inline(line[3:]),styles['Heading2']))
        elif line.startswith('- '):
            story.append(Paragraph('- '+inline(line[2:]),body))
        else:
            story.append(Paragraph(inline(line),body))
        i+=1


def footer(canvas,doc):
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#617366'))
    canvas.drawString(44,26,'Investment Memory Engine | PostgreSQL + Chroma + Next.js')
    canvas.drawRightString(A4[0]-44,26,str(doc.page))


def main():
    for index,name in enumerate(['PROJECT_REPORT.md','DATABASE_DESIGN.md','REQUIREMENTS_COMPLIANCE.md','TEAM.md','TEST_RESULTS.md','DEMO_GUIDE.md']):
        if index:
            story.append(PageBreak())
        add_markdown(ROOT/'docs'/name)
    captures=sorted((ROOT/'docs/screenshots').glob('nextjs_*.png'))
    if captures:
        story.append(PageBreak())
        story.append(Paragraph('Next.js application screenshots',styles['Title']))
        for path in captures:
            story.append(Paragraph(escape(path.stem.replace('_',' ')),styles['Heading2']))
            image=Image(str(path))
            scale=min((A4[0]-88)/image.imageWidth,580/image.imageHeight)
            image.drawWidth=image.imageWidth*scale
            image.drawHeight=image.imageHeight*scale
            story.append(image)
            story.append(PageBreak())
    old=ROOT/'PROJECT_REPORT.pdf'
    archive=ROOT/'legacy/PROJECT_REPORT_SQLITE.pdf'
    if old.exists() and not archive.exists():
        shutil.copy2(old,archive)
    SimpleDocTemplate(str(old),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=42,bottomMargin=45,
                      title='Investment Memory Engine Level 3 Project Report',
                      author='S Anuj Srijan PES1UG24AM234; Aswin Adhitya PES1UG24AM213').build(story,onFirstPage=footer,onLaterPages=footer)
    import pymupdf
    diagram = pymupdf.open(ROOT/'diagrams/erdiagram.png')
    diagram_pdf = pymupdf.open('pdf', diagram.convert_to_pdf())
    report = pymupdf.open(old)
    report.insert_pdf(diagram_pdf)
    merged = old.with_name('PROJECT_REPORT.build.pdf')
    report.save(merged)
    report.close()
    merged.replace(old)
    print('Built PROJECT_REPORT.pdf with current ER diagram')


if __name__=='__main__':
    main()
