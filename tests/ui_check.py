"""Exercise the real Streamlit script with its built-in test runner."""
import os
from pathlib import Path
import sys
import tempfile
from streamlit.testing.v1 import AppTest

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
    os.environ["IME_DATA_DIR"] = folder
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    app = AppTest.from_file(str(root / "app.py"), default_timeout=30).run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 8
    app.sidebar.radio[0].set_value("SQL Reports").run()
    assert not app.exception
    assert len(app.dataframe) == 3
    app.sidebar.radio[0].set_value("Search Memories").run()
    assert not app.exception
    app.text_input[0].set_value(" ").run()
    app.button[0].click().run()
    assert app.error
    app.sidebar.radio[0].set_value("Add Investment Memory").run()
    app.button[0].click().run()
    assert app.error
    assert len(app.dataframe[0].value) == 8
    print("PASS: three pages, seed table, SQL report tables, blank search, invalid save.")
