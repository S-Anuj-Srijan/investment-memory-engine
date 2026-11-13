"""Real PostgreSQL integration tests in a unique disposable schema.

Set TEST_DATABASE_URL to a PostgreSQL database where CREATE SCHEMA is allowed.
No existing tables or records are modified. Chroma uses a temporary directory.
"""
import os
import tempfile
import unittest
import uuid
from unittest.mock import patch

import psycopg
from psycopg.conninfo import make_conninfo
from fastapi.testclient import TestClient

from backend import db, security, vectors
from backend.api import app, attempts

URL = os.environ.get('TEST_DATABASE_URL')


class SecurityTests(unittest.TestCase):
    def test_local_browser_origins(self):
        with patch.dict(os.environ, {'APP_ORIGIN':'http://localhost:3000'}), TestClient(app) as client:
            for origin in ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://[::1]:3000']:
                # Invalid input stops before touching the database, after origin validation.
                self.assertEqual(client.post('/api/setup', json={}, headers={'Origin':origin}).status_code,422)
            for origin in ['http://localhost:3001', 'https://localhost:3000', 'http://localhost.attacker.com:3000', 'null']:
                self.assertEqual(client.post('/api/setup', json={}, headers={'Origin':origin}).status_code,403)
            self.assertEqual(client.post('/api/setup', json={}).status_code,403)
        with patch.dict(os.environ, {'APP_ORIGIN':'https://example.com'}), TestClient(app) as client:
            self.assertEqual(client.post('/api/setup', json={}, headers={'Origin':'http://localhost:3000'}).status_code,403)
            self.assertEqual(client.post('/api/setup', json={}, headers={'Origin':'https://example.com'}).status_code,422)

    def test_salted_hashes(self):
        first = security.hash_password('A-long-test-password')
        self.assertNotEqual(first, security.hash_password('A-long-test-password'))
        self.assertTrue(security.verify_password('A-long-test-password', first))
        self.assertFalse(security.verify_password('wrong', first))
        with self.assertRaises(ValueError):
            security.hash_password('short')


@unittest.skipUnless(URL, 'Set TEST_DATABASE_URL to run real PostgreSQL tests')
class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = 'test_ime_' + uuid.uuid4().hex
        with psycopg.connect(URL, autocommit=True) as conn:
            conn.execute(f'CREATE SCHEMA {cls.schema}')
        cls.folder = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        cls.env = patch.dict(os.environ, {
            'DATABASE_URL': make_conninfo(URL, options=f'-c search_path={cls.schema},public'),
            'CHROMA_PATH': cls.folder.name, 'APP_ORIGIN':'http://localhost:3000'})
        cls.env.start()
        db.initialize()
        with db.connect() as conn:
            for name,role in [('Admin','admin'),('Analyst','analyst'),('Other','analyst')]:
                conn.execute('INSERT INTO users(email,display_name,password_hash,role) VALUES (%s,%s,%s,%s)',
                             (name.lower()+'@test.local',name,security.hash_password('Integration-password-123'),role))

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        vectors.collection.cache_clear()
        with psycopg.connect(URL, autocommit=True) as conn:
            conn.execute(f'DROP SCHEMA {cls.schema} CASCADE')
        cls.folder.cleanup()

    def client(self, name='admin'):
        attempts.clear()
        client = TestClient(app, headers={'Origin':'http://localhost:3000'})
        result = client.post('/api/login', json={'email':name+'@test.local','password':'Integration-password-123'})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertIn('HttpOnly',result.headers['set-cookie'])
        return client

    def payload(self, **changes):
        data = dict(company_id=1, model_id=1, headline='AI infrastructure expands',
                    news_text='New data centers need AI accelerator chips.',
                    reasoning_text='Increased AI spending may support GPU demand.', amount=2500,
                    decision='BUY', trade_date='2026-11-01',published_at='2026-10-31',confidence=.8,
                    return_percentage=None)
        data.update(changes)
        return data

    def test_01_seed_reports_and_ddl(self):
        db.initialize()
        self.assertEqual(len(db.rows('SELECT * FROM memory_details')),8)
        client = self.client()
        reports = client.get('/api/reports').json()
        self.assertEqual(len(reports),6)
        self.assertEqual(reports[0]['rows'][0]['company_name'],'NVIDIA')
        self.assertEqual(float(reports[0]['rows'][0]['avg_return_pct']),6)
        with db.connect() as conn:
            # Execute standalone lab including its transaction; user data is unaffected.
            conn.execute((db.ROOT/'sql/06_advanced_demo.sql').read_text())
        self.assertEqual(len(db.rows('SELECT * FROM memory_details')),8)

    def test_02_authentication_authorization_and_csrf(self):
        anonymous = TestClient(app)
        self.assertEqual(anonymous.get('/api/memories').status_code,401)
        self.assertEqual(anonymous.post('/api/logout').status_code,403)
        client = self.client('analyst')
        for path, method in [('/api/audit','get'),('/api/index/rebuild','post'),('/api/memories/1','delete')]:
            self.assertEqual(getattr(client,method)(path).status_code,403)
        self.assertEqual(client.patch('/api/memories/1',json={'revision':1,'return_percentage':3}).status_code,403)
        self.assertEqual(client.post('/api/users',json={'email':'new@test.local','display_name':'New','password':'Some-long-password','role':'admin'}).status_code,403)
        client.post('/api/logout')
        self.assertEqual(client.get('/api/me').status_code,401)
        attempts.clear()
        for _ in range(10):
            self.assertEqual(client.post('/api/login',json={'email':'nobody@test.local','password':'wrong'}).status_code,401)
        self.assertEqual(client.post('/api/login',json={'email':'nobody@test.local','password':'wrong'}).status_code,429)

    def test_03_transaction_constraints(self):
        client = self.client()
        before = [db.rows('SELECT COUNT(*) AS n FROM '+t)[0]['n'] for t in ['companies','news','investments']]
        response = client.post('/api/memories',json=self.payload(company_id=None,company_name='Rollback test',ticker='ROLLBACK',sector='Test',model_id=999999))
        self.assertEqual(response.status_code,409)
        self.assertEqual(before,[db.rows('SELECT COUNT(*) AS n FROM '+t)[0]['n'] for t in ['companies','news','investments']])
        for change in [{'amount':0},{'confidence':1.1},{'decision':'INVALID'},{'headline':' '},{'trade_date':'invalid'},{'return_percentage':-101}]:
            self.assertEqual(client.post('/api/memories',json=self.payload(**change)).status_code,422)
        for sql in ["UPDATE investments SET investment_amount=-1 WHERE investment_id=1",
                    "UPDATE investment_reasoning SET confidence=2 WHERE reasoning_id=1",
                    "UPDATE investments SET company_id=999999 WHERE investment_id=1",
                    "UPDATE news SET headline=' ' WHERE news_id=1",
                    "UPDATE investments SET investment_amount='NaN' WHERE investment_id=1"]:
            with self.assertRaises(psycopg.IntegrityError):
                with db.connect() as conn:
                    conn.execute(sql)

    def test_04_crud_audit_and_concurrent_update(self):
        analyst = self.client('analyst')
        response = analyst.post('/api/memories',json=self.payload())
        self.assertEqual(response.status_code,201,response.text)
        rid=response.json()['reasoning_id']
        other=self.client('other')
        self.assertEqual(other.patch(f'/api/memories/{rid}',json={'revision':1,'return_percentage':4}).status_code,403)
        self.assertEqual(analyst.patch(f'/api/memories/{rid}',json={'revision':1,'return_percentage':4}).status_code,200)
        self.assertEqual(analyst.patch(f'/api/memories/{rid}',json={'revision':1,'return_percentage':5}).status_code,409)
        admin=self.client()
        self.assertEqual(admin.delete(f'/api/memories/{rid}').status_code,200)
        self.assertEqual(admin.delete(f'/api/memories/{rid}').status_code,404)
        events=admin.get('/api/audit').json()
        self.assertEqual({e['operation'] for e in events if e['actor_id'] is not None},{'INSERT','UPDATE','DELETE'})
        self.assertEqual(len(db.rows('SELECT * FROM memory_details')),8)

    def test_05_filters_users_and_sessions(self):
        client=self.client()
        rows=client.get('/api/memories?sector=Finance&decision=BUY').json()
        self.assertEqual(len(rows),2)
        self.assertEqual(client.get('/api/memories',params={'sector':"' OR 1=1 --"}).json(),[])
        data={'email':'new@test.local','display_name':'New','password':'Some-long-password','role':'analyst'}
        self.assertEqual(client.post('/api/users',json=data).status_code,201)
        self.assertEqual(client.post('/api/users',json=data).status_code,409)
        with db.connect() as conn:
            conn.execute("UPDATE sessions SET expires_at=now()-interval '1 second'")
        self.assertEqual(client.get('/api/me').status_code,401)

    @unittest.skipUnless(os.environ.get('TEST_VECTORS')=='1','Set TEST_VECTORS=1 for real MiniLM/Chroma test')
    def test_06_real_vector_search_and_staleness(self):
        vectors.collection.cache_clear()
        self.assertEqual(vectors.rebuild(),8)
        self.assertEqual(vectors.status()['pending'],0)
        hits=vectors.search('Companies benefiting from increased AI infrastructure spending')
        self.assertTrue(any(r['ticker'] in {'NVDA','AMD'} for r in hits))
        for row in hits:
            self.assertAlmostEqual(row['similarity'],1-row['distance'])
        client=self.client()
        rid=client.post('/api/memories',json=self.payload()).json()['reasoning_id']
        self.assertEqual(vectors.status()['pending'],1)
        vectors.rebuild()
        client.delete(f'/api/memories/{rid}')
        self.assertTrue(all(r['reasoning_id']!=rid for r in vectors.search('AI demand')))
        self.assertEqual(vectors.status()['stale'],1)
        vectors.rebuild()
        self.assertEqual(vectors.status()['stale'],0)
        # A direct text edit must not return an obsolete embedding.
        with db.connect() as conn:
            conn.execute("UPDATE investment_reasoning SET reasoning_text=reasoning_text || ' Updated.' WHERE reasoning_id=1")
        self.assertEqual(vectors.status()['pending'],1)
        self.assertTrue(all(r['reasoning_id']!=1 for r in vectors.search('AI demand')))
        vectors.rebuild()
        self.assertEqual(vectors.status()['pending'],0)


@unittest.skipUnless(URL, 'Set TEST_DATABASE_URL to run real PostgreSQL tests')
class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.schema = 'test_setup_' + uuid.uuid4().hex
        with psycopg.connect(URL, autocommit=True) as conn:
            conn.execute(f'CREATE SCHEMA {self.schema}')
        self.env = patch.dict(os.environ, {
            'DATABASE_URL': make_conninfo(URL, options=f'-c search_path={self.schema},public'),
            'APP_ORIGIN': 'http://localhost:3000'})
        self.env.start()
        db.initialize()
        self.client = TestClient(app, headers={'Origin': 'http://localhost:3000'})
        self.payload = {'email': 'first@test.local', 'display_name': 'First Admin',
                        'password': 'A-long-setup-password', 'confirm_password': 'A-long-setup-password'}

    def tearDown(self):
        self.client.close()
        self.env.stop()
        with psycopg.connect(URL, autocommit=True) as conn:
            conn.execute(f'DROP SCHEMA {self.schema} CASCADE')

    def test_setup_login_and_permanent_closure(self):
        self.assertTrue(self.client.get('/api/setup').json()['required'])
        result = self.client.post('/api/setup', json=self.payload)
        self.assertEqual(result.status_code, 201, result.text)
        self.assertNotIn('password', result.text)
        self.assertFalse(self.client.get('/api/setup').json()['required'])
        self.assertEqual(self.client.post('/api/setup', json={**self.payload, 'email':'second@test.local'}).status_code,409)
        account = db.rows('SELECT * FROM users')[0]
        self.assertEqual(account['role'],'admin')
        self.assertTrue(security.verify_password(self.payload['password'], account['password_hash']))
        attempts.clear()
        response = self.client.post('/api/login', json={'email':self.payload['email'],'password':self.payload['password']})
        self.assertEqual(response.status_code,200)
        self.assertEqual(self.client.get('/api/me').json()['role'],'admin')

    def test_setup_validation_and_origin(self):
        for changes in [{'password':'short','confirm_password':'short'},
                        {'confirm_password':'A-different-password'}, {'display_name':'   '},
                        {'email':'invalid'}, {'role':'admin'}]:
            response=self.client.post('/api/setup',json={**self.payload,**changes})
            self.assertEqual(response.status_code,422,response.text)
        response=self.client.post('/api/setup',json=self.payload,headers={'Origin':'http://untrusted.local'})
        self.assertEqual(response.status_code,403)
        self.assertEqual(db.rows('SELECT COUNT(*) AS n FROM users')[0]['n'],0)

    def test_concurrent_setup_creates_one_admin(self):
        from concurrent.futures import ThreadPoolExecutor
        def create(email):
            with TestClient(app,headers={'Origin':'http://localhost:3000'}) as client:
                return client.post('/api/setup',json={**self.payload,'email':email}).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            codes=list(pool.map(create,['one@test.local','two@test.local']))
        self.assertEqual(sorted(codes),[201,409])
        self.assertEqual(db.rows('SELECT COUNT(*) AS n FROM users')[0]['n'],1)


if __name__=='__main__':
    unittest.main(verbosity=2)
