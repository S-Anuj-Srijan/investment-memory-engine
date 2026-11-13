"""Build the academic report from original diagrams, SQL and real screenshots."""
from pathlib import Path
import sys
from html import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, Preformatted

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import database

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=11, leading=16, spaceAfter=10))
styles.add(ParagraphStyle(name="SmallNote", fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#475569")))
styles.add(ParagraphStyle(name="CodeSmall", fontName="Courier", fontSize=8, leading=11))
story = []
W, H = landscape(A4)
usable = W-96

def p(text, style="Body"):
    story.append(Paragraph(text, styles[style]))

def title(text):
    p(text, "Heading1")
    story.append(Spacer(1, 8))

def new():
    story.append(PageBreak())

def picture(path, height=390):
    im = Image(str(path))
    scale = min(usable/im.imageWidth, height/im.imageHeight)
    im.drawWidth = im.imageWidth*scale
    im.drawHeight = im.imageHeight*scale
    story.append(im)

def table(headers, records, widths):
    data = [[Paragraph(escape(str(v)), styles["SmallNote"]) for v in headers]]
    data.extend([[Paragraph(escape(str(v)), styles["SmallNote"]) for v in row] for row in records])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e2e8f0")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("BOTTOMPADDING",(0,0),(-1,-1),9),
        ("TOPPADDING",(0,0),(-1,-1),9),
        ("LINEBELOW",(0,0),(-1,0),0.8,colors.HexColor("#94a3b8")),
        ("LINEBELOW",(0,1),(-1,-1),0.3,colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)

def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.line(48,35,W-48,35)
    canvas.setFont("Helvetica",8)
    canvas.setFillColor(colors.HexColor("#475569"))
    canvas.drawString(48,23,"Investment Memory Engine | DBMS Laboratory")
    canvas.drawRightString(W-48,23,str(doc.page))

story.append(Spacer(1,55))
p("INVESTMENT MEMORY ENGINE", "Title")
p("A simple hybrid RDBMS + NoSQL mini-project", "Heading2")
story.append(Spacer(1,28))
table(["Student", "SRN"], [
    ["S Anuj Srijan","PES1UG24AM234"],
    ["Aswin Adhitya","PES1UG24AM213"],
], [usable*0.55,usable*0.45])
story.append(Spacer(1,22))
p("Academic project report | 26 October 2026")
p("Python + Streamlit + SQLite + ChromaDB + Sentence Transformers")
p("All sample news, decisions, explanations and returns are fictional demonstration data. "
  "The project does not execute trades or claim predictive investment performance.", "SmallNote")

new()
title("1. Abstract and introduction")
p("Investment Memory Engine stores both an investment transaction and its surrounding context. "
  "SQLite preserves companies, model labels, news, investments and reasoning in five related tables. "
  "ChromaDB stores embeddings of the headline, news content and explanation, allowing natural-language "
  "retrieval of similar past contexts. The retrieved vector metadata links back to the structured investment and return.")
p("A conventional investment record answers what was bought, when, for how much and with what return. "
  "This project also records the supplied explanation and relevant news. Users enter simulated model outputs manually; "
  "the system does not invoke an external language model.")
title("2. Problem statement and objectives")
p("Problem: numerical transaction records alone make it difficult to find earlier investments with a similar news context or decision rationale.")
p("Objectives: implement five relational tables with enforced keys; maintain a local semantic memory collection; "
  "retrieve structured and vector records together; execute three SQL reports; and provide a small interface suitable for a DBMS viva.")
title("3. Technologies")
table(["Technology","Role"],[
    ["Python / Streamlit","Validation, application logic and three sidebar pages"],
    ["SQLite (sqlite3)","Persistent structured records, transactions, constraints and SQL reports"],
    ["ChromaDB","Local vector collection investment_memories with cosine distance"],
    ["Sentence Transformers","Pretrained all-MiniLM-L6-v2; local 384-dimensional text embeddings"],
], [190,usable-190])

new()
title("4. Latest handwritten ER and architecture reference")
p("Preferred original handwritten PNG, embedded without redrawing. Its abbreviated names and illustrative values "
  "are visual notes; the supplied SQL defines the implemented column names and demonstration data.", "SmallNote")
picture(ROOT/"diagrams/03_latest_handwritten_reference.png",390)

new()
title("5. ER diagram - preserved supporting reference")
picture(ROOT/"diagrams/01_handdrawn_ER_diagram.png",395)
p("Earlier hand-drawn-style reference preserved as supplied. The Chroma link is an application-level ID link, not a SQL foreign key.", "SmallNote")

new()
title("6. System architecture - preserved supporting reference")
picture(ROOT/"diagrams/02_handdrawn_architecture.png",395)
p("SQLite is the source of truth. ChromaDB is a rebuildable semantic index. Both stores run locally after initial setup.", "SmallNote")

new()
title("7. Five-table relational design")
table(["Table","Columns and keys"],[
    ["companies","company_id PK; company_name; ticker UNIQUE; sector"],
    ["models","model_id PK; model_name; version"],
    ["news","news_id PK; headline; news_text; published_at; source"],
    ["investments","investment_id PK; company_id FK; model_id FK; investment_amount; decision; trade_date; return_percentage"],
    ["investment_reasoning","reasoning_id PK; investment_id FK; news_id FK; reasoning_text; confidence; vector_memory_id UNIQUE"],
], [160,usable-160])
story.append(Spacer(1,12))
p("Relationships: companies 1:N investments; models 1:N investments; investments 1:N investment_reasoning; "
  "news 1:N investment_reasoning. Separate company/model tables reduce repeated descriptive data. "
  "Each reasoning row references one news item and one investment.")
p("Constraints: amount must be positive; confidence is NULL or between 0 and 1; ticker and vector ID are unique. "
  "The original schema allows BUY, SELL and HOLD; the requested interface offers BUY/SELL. Unknown returns are NULL.")
p("Every connection enables PRAGMA foreign_keys=ON. New company, news, investment and reasoning inserts share "
  "one SQLite transaction. A failure rolls them all back. Initialization checks all five tables under a write lock and seeds only when empty.")

new()
title("8. RDBMS and NoSQL integration")
p("<b>Save:</b> validate inputs; commit structured rows to SQLite; combine headline, news_text and reasoning_text; "
  "generate a normalized MiniLM embedding; upsert into Chroma using vector_memory_id. Metadata stores integer reasoning_id.")
p("<b>Search:</b> embed the query using the same model, retrieve up to three nearest vectors, and join the metadata "
  "reasoning_id through investment_reasoning, investments, companies, models and news. Return values always come from SQLite.")
p("<b>Metric:</b> cosine similarity = 1 - cosine distance. Higher similarity means closer text meaning. "
  "The score is not investment confidence, a probability of profit, or a forecast.")
p("<b>Recovery:</b> there is no atomic transaction across SQLite and ChromaDB. If indexing fails after SQL commits, "
  "the interface reports a saved but unindexed memory. Rebuild the index instead of submitting again. Stable IDs and "
  "upsert make repairs repeatable; stale vector IDs are removed during rebuilding.")
title("9. Project novelty and limitations")
p("The distinguishing feature is searchable decision context: why an investment was chosen and which news supported "
  "the explanation. This combines relational reporting with semantic retrieval; it does not claim to invent vector search.")
p("The dataset is synthetic, explanations are manually supplied, and similarity is not causal evidence. "
  "Long input may be truncated by the embedding model. The project is intended for one local lab user. "
  "Attention weights are not a database storage format; the application stores text embeddings.")

new()
title("10. SQL queries")
p("Executed directly from sql/05_reports.sql. Results are computed from SQLite, not hardcoded.")
for i, query in enumerate((ROOT/"sql/05_reports.sql").read_text().split(";")[:3],1):
    p("Report " + str(i), "Heading3")
    story.append(Preformatted(query.strip()+";", styles["CodeSmall"]))

new()
title("11. Demonstration dataset and expected SQL results")
p("The supplied seed contains 5 companies, 2 model labels, 6 news items, 8 investments and 8 reasoning rows. "
  "All monetary amounts and returns below are simulated. These expected results describe the original seed.")
table(["Report","Expected seed output"], [
    ["Average return by company","NVIDIA 6.00%; Microsoft 3.00%; JPMorgan Chase 1.75%; AMD 1.50%; Exxon Mobil -1.50%"],
    ["Investment count by sector","Technology: 5; Finance: 2; Energy: 1"],
    ["Top five returns","8.00%, 5.00%, 4.00%, 3.00%, 2.50%"],
], [210,usable-210])
story.append(Spacer(1,15))
p("Example memory: NVIDIA; INR 10,000; BUY on 2026-08-02; fictional return 8%. News: AI-chip demand rises. "
  "Explanation: rising AI data-center demand could support GPU revenue. Vector ID: memory_1.")
title("12. Five-minute demonstration")
p("1. Show the five tables and explain primary/foreign keys.<br/>"
  "2. Show eight saved memories in Add Investment Memory.<br/>"
  "3. Search 'Companies benefiting from increased AI infrastructure spending' and inspect context, decision and return.<br/>"
  "4. Add one fictional memory, then search a related idea.<br/>"
  "5. Open the three SQL reports and expand each query.<br/>"
  "6. Explain the SQL-to-vector ID link, cosine similarity and index recovery.")

new()
title("13. Testing and verification status")
p("Relational checks passed: exactly five tables, eight seed memories, repeatable initialization, foreign-key rejection, "
  "correct expected SQL report results, input validation, transaction rollback, and a new saved memory.")
p("Streamlit's built-in AppTest passed for all three pages, the seeded records display, three report tables, "
  "blank-search validation and invalid-save validation.")
p("Environment limitation: ChromaDB and Sentence Transformers were not installed. Package installation failed because "
  "network socket access was blocked. Therefore real embedding generation, eight indexed vectors, semantic relevance "
  "and full cross-store saves remain unverified. No vector success is claimed.")
p("The installed Streamlit environment also contained an outdated Tornado package. The application was launched using "
  "a compatible locally cached Tornado package for UI inspection. A fresh virtual environment is recommended.")
p("tests/smoke_check.py includes full vector checks to run after installation; --sql-only explicitly skips vector checks. "
  "Tests use disposable databases and do not alter the user's saved sample data.")
title("14. Application screenshots")
p("Only actual browser captures are included on the following pages when available. A missing-dependency search screen "
  "is labeled as such and is not evidence of successful semantic retrieval.")
screens = [
    ("01_add.png","Add Investment Memory - actual running interface"),
    ("02_reports.png","SQL Reports - actual results from SQLite"),
    ("03_search_setup.png","Search Memories - setup warning; semantic results not verified"),
]
for name, caption in screens:
    file = ROOT/"docs/screenshots"/name
    if file.exists():
        new()
        title(caption)
        picture(file,415)
    else:
        p("Capture unavailable: " + caption + ". No screenshot has been fabricated.", "SmallNote")

new()
title("15. Setup and conclusion")
p("From PowerShell in the project folder:")
story.append(Preformatted(
    "python -m venv .venv\n"
    ".\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n"
    ".\\.venv\\Scripts\\python.exe init_db.py\n"
    ".\\.venv\\Scripts\\python.exe tests/smoke_check.py\n"
    ".\\.venv\\Scripts\\python.exe -m streamlit run app.py", styles["CodeSmall"]))
story.append(Spacer(1,12))
p("Initial setup needs internet to install packages and download the pretrained model. Retain data/model_cache "
  "for subsequent offline operation. Repair indexing with python init_db.py --rebuild-index.")
p("Investment Memory Engine demonstrates a compact hybrid database design: SQLite preserves reliable structured "
  "facts and reports, while ChromaDB provides a semantic retrieval path over stored context. The relational and interface "
  "checks are complete; full vector verification must be completed in an environment with the required dependencies.")
title("Source materials")
p("Original project README and CODEX_PROMPT.txt; sql/03_schema.sql, sql/04_demo_data.sql, sql/05_reports.sql; "
  "all three original PNGs in diagrams/; docs/06_project_deliverables.pdf (preserved draft).", "SmallNote")
p("Implementation references: Chroma collection documentation (cookbook.chromadb.dev/core/collections/) and "
  "Sentence Transformers API documentation (sbert.net/docs/package_reference/sentence_transformer/).", "SmallNote")

SimpleDocTemplate(str(ROOT/"PROJECT_REPORT.pdf"), pagesize=(W,H), rightMargin=48,
                  leftMargin=48, topMargin=40, bottomMargin=48,
                  title="Investment Memory Engine", author="S Anuj Srijan; Aswin Adhitya").build(
                      story, onFirstPage=footer, onLaterPages=footer)
print(ROOT/"PROJECT_REPORT.pdf")
