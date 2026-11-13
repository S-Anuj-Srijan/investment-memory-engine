import os
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')


@contextmanager
def connect(actor=None):
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise RuntimeError('Set DATABASE_URL in .env before starting the API.')
    with psycopg.connect(url, row_factory=dict_row, connect_timeout=10) as conn:
        if actor is not None:
            conn.execute("SELECT set_config('app.actor_id', %s, true)", (str(actor),))
        yield conn


def rows(query, params=()):
    with connect() as conn:
        return conn.execute(query, params).fetchall()


def initialize(seed=True):
    with connect() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(7462301)")
        conn.execute((ROOT / 'sql/03_schema.sql').read_text())
        if seed and not conn.execute('SELECT 1 FROM companies LIMIT 1').fetchone():
            conn.execute((ROOT / 'sql/04_demo_data.sql').read_text())
            for table, key in [('companies','company_id'), ('models','model_id'),
                               ('news','news_id'), ('investments','investment_id'),
                               ('investment_reasoning','reasoning_id')]:
                conn.execute(f"SELECT setval(pg_get_serial_sequence('{table}', '{key}'), (SELECT MAX({key}) FROM {table}))")
