"""Archived SQLite/Streamlit prototype.

The current Level 3 application is web/ (Next.js) plus backend/ (PostgreSQL).
Run ./start_project.ps1 from the project root to start that application.
"""
import sqlite3
from datetime import date
import streamlit as st
import database
import vector_store

st.set_page_config(page_title="Investment Memory Engine", page_icon="📘", layout="wide")
st.warning("Legacy SQLite/Streamlit prototype. For the current Level 3 project, "
           "run ./start_project.ps1 and open http://localhost:3000.")
try:
    database.initialize()
except Exception as exc:
    st.error("Could not initialize SQLite: " + str(exc))
    st.stop()

st.sidebar.title("Investment Memory Engine")
page = st.sidebar.radio("Navigation", ["Add Investment Memory", "Search Memories", "SQL Reports"])
st.sidebar.caption("SQLite: structured records and SQL reports.\n\nChromaDB: text embeddings and semantic search.")
st.sidebar.info("Demonstration only. News, reasoning and returns are fictional.")
st.title(page)
st.caption("Preserve the decision, its context, and its eventual outcome.")
st.caption("No live trading or AI-generated advice. Model explanations are entered manually.")

if page == "Add Investment Memory":
    companies = database.rows("SELECT * FROM companies ORDER BY company_name")
    models = database.rows("SELECT * FROM models ORDER BY model_id")
    with st.form("add_memory", clear_on_submit=False):
        left, right = st.columns(2)
        with left:
            company = st.selectbox("Company", [None] + [c["company_id"] for c in companies],
                format_func=lambda v: "New company" if v is None else next(c["company_name"] for c in companies if c["company_id"] == v))
            st.caption("Fill these three fields only when adding a new company.")
            name = st.text_input("New company name")
            ticker = st.text_input("New company ticker")
            sector = st.text_input("New company sector")
            amount = st.number_input("Investment amount (INR)", min_value=0.01, value=10000.0, step=100.0)
            trade_date = st.date_input("Investment date", value=date.today())
            decision = st.selectbox("Decision", ["BUY", "SELL"])
        with right:
            model_id = st.selectbox("Model name", [m["model_id"] for m in models],
                format_func=lambda v: next(m["model_name"] + " / " + m["version"] for m in models if m["model_id"] == v))
            headline = st.text_input("News headline")
            news_text = st.text_area("News content")
            published_at = st.date_input("News publication date", value=date.today())
            reasoning = st.text_area("Investment reasoning")
            confidence = st.slider("Confidence (entered value, not calculated)", 0.0, 1.0, 0.75)
            known_return = st.checkbox("Return is known")
            return_value = st.number_input("Return percentage (fictional)", value=0.0, step=0.1)
        submitted = st.form_submit_button("Save Investment Memory", type="primary")
    if submitted:
        try:
            reasoning_id = database.save_memory(company_id=company, company_name=name, ticker=ticker,
                sector=sector, model_id=model_id, headline=headline, news_text=news_text,
                reasoning_text=reasoning, amount=amount, decision=decision, trade_date=trade_date,
                published_at=published_at, confidence=confidence,
                return_percentage=return_value if known_return else None)
        except (ValueError, sqlite3.Error) as exc:
            st.error("Nothing saved: " + str(exc))
        else:
            try:
                with st.spinner("Creating the text embedding and saving to ChromaDB..."):
                    vector_store.index_memories([database.memory(reasoning_id)])
                st.success("Memory saved in SQLite and indexed in ChromaDB.")
            except Exception as exc:
                st.warning("Memory saved in SQLite, but not confirmed in ChromaDB. Do not submit again. "
                           "Run python init_db.py --rebuild-index to repair the index.")
                st.error(str(exc))
    with st.expander("View saved demonstration memories", expanded=True):
        records = database.memories()
        st.caption(str(len(records)) + " stored memories")
        st.dataframe([{k:r[k] for k in ("company_name", "ticker", "decision", "investment_amount",
                       "trade_date", "return_percentage")} for r in records], hide_index=True, width="stretch")

elif page == "Search Memories":
    st.info("Example: Companies benefiting from increased AI infrastructure spending")
    st.caption("Cosine similarity = 1 - cosine distance. Higher similarity means closer text meaning "
               "(range -1 to 1); it is not a probability or a predicted return.")
    try:
        pending = vector_store.pending_count()
        if pending:
            st.warning(str(pending) + " SQL memories need indexing. Run python init_db.py --rebuild-index.")
    except Exception as exc:
        st.warning(str(exc))
    with st.form("search"):
        query = st.text_input("Describe an investment idea", value="Companies benefiting from increased AI infrastructure spending")
        searched = st.form_submit_button("Search Memories", type="primary")
    if searched:
        try:
            with st.spinner("Finding related memories..."):
                matches = vector_store.search(query)
            if not matches:
                st.info("No linked memories found. Rebuild the index from SQLite.")
            for row in matches:
                with st.container(border=True):
                    st.subheader(row["company_name"] + " (" + row["ticker"] + ")")
                    st.write("**News:** " + row["headline"])
                    st.write(row["news_text"])
                    st.write("**Model reasoning:** " + row["reasoning_text"])
                    st.write("**Model:** " + row["model_name"] + " / " + row["version"])
                    value = row["return_percentage"]
                    st.write(f"**Decision:** {row['decision']} | **Amount:** INR {row['investment_amount']:,.2f}"
                             f" | **Return:** {'Unknown' if value is None else str(value) + '% (fictional)'}")
                    st.caption(f"Cosine similarity: {row['similarity']:.4f} | Distance: {row['distance']:.4f}"
                               f" | Memory: {row['vector_memory_id']}")
        except Exception as exc:
            st.error(str(exc))
else:
    titles = ["Average investment return by company", "Total investments by sector",
              "Top five investments ranked by return"]
    st.caption("Computed from SQLite now. All returns are fictional; unknown returns are excluded from averages and rankings.")
    for title, (sql, records) in zip(titles, database.reports()):
        st.subheader(title)
        st.dataframe(records, hide_index=True, width="stretch")
        with st.expander("View SQL: " + title):
            st.code(sql, language="sql")
