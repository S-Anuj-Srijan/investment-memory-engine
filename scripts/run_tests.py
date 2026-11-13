"""Run integration tests in an isolated PostgreSQL schema using local .env."""
import os
from pathlib import Path
import sys
import unittest
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
load_dotenv(ROOT/'.env')
if not os.environ.get('DATABASE_URL'):
    raise SystemExit('Configure .env and start PostgreSQL first.')
os.environ.setdefault('TEST_DATABASE_URL',os.environ['DATABASE_URL'])
if '--vectors' in sys.argv:
    os.environ['TEST_VECTORS']='1'
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_backend.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
