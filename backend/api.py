import logging
import os
import secrets
import time
from collections import defaultdict, deque
from datetime import date
from threading import Lock
from typing import Literal
from urllib.parse import urlsplit

import psycopg
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from . import db, security, vectors

app = FastAPI(title='Investment Memory Engine', docs_url='/api/docs', openapi_url='/api/openapi.json')
COOKIE = 'ime_session'
attempts = defaultdict(deque)
attempt_lock = Lock()
DUMMY_HASH = security.hash_password(secrets.token_urlsafe(24))


def allowed_browser_origins():
    configured = os.environ.get('APP_ORIGIN', 'http://localhost:3000').strip().rstrip('/')
    origins = {configured}
    parsed = urlsplit(configured)
    # The launcher binds to loopback; both names refer to this same local app.
    # Keep the configured scheme and port, never trust arbitrary Host headers.
    if parsed.hostname in {'localhost', '127.0.0.1', '::1'}:
        port = f':{parsed.port}' if parsed.port else ''
        origins.update(f'{parsed.scheme}://{host}{port}'
                       for host in ('localhost', '127.0.0.1', '[::1]'))
    return origins


@app.middleware('http')
async def browser_security(request, call_next):
    if request.method in {'POST','PUT','PATCH','DELETE'}:
        if request.headers.get('origin') not in allowed_browser_origins():
            return JSONResponse({'detail': 'Request origin is not allowed. Open the application at the APP_ORIGIN address configured in .env.'}, status_code=403)
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.exception_handler(psycopg.IntegrityError)
async def integrity_error(request, exc):
    return JSONResponse({'detail': 'Database constraint rejected the operation. Check references, unique values and ranges.'}, status_code=409)


@app.exception_handler(psycopg.OperationalError)
async def connection_error(request, exc):
    return JSONResponse({'detail': 'PostgreSQL is unavailable. Check server configuration.'}, status_code=503)


def current_user(request: Request):
    token = request.cookies.get(COOKIE, '')
    result = db.rows('SELECT u.user_id,u.email,u.display_name,u.role FROM sessions s JOIN users u USING(user_id) WHERE token_hash=%s AND expires_at>now()',
                     (security.token_hash(token),))
    if not result:
        raise HTTPException(401, 'Sign in to continue.')
    return result[0]


def admin(user=Depends(current_user)):
    if user['role'] != 'admin':
        raise HTTPException(403, 'Administrator access required.')
    return user


class Input(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid', allow_inf_nan=False)


class Login(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)


class MemoryInput(Input):
    company_id: int | None = Field(default=None, gt=0)
    company_name: str = Field(default='', max_length=150)
    ticker: str = Field(default='', max_length=15, pattern=r'^[A-Za-z0-9.-]*$')
    sector: str = Field(default='', max_length=100)
    model_id: int = Field(gt=0)
    headline: str = Field(min_length=1, max_length=300)
    news_text: str = Field(min_length=1, max_length=12000)
    reasoning_text: str = Field(min_length=1, max_length=12000)
    amount: float = Field(gt=0, lt=100000000000000)
    decision: Literal['BUY','SELL','HOLD']
    trade_date: date
    published_at: date
    confidence: float = Field(ge=0, le=1)
    return_percentage: float | None = Field(default=None, ge=-100, le=100000)


class Outcome(Input):
    return_percentage: float | None = Field(default=None, ge=-100, le=100000)
    revision: int = Field(gt=0)


class AccountInput(Input):
    # Passwords must retain the exact characters entered by the administrator.
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)
    email: str = Field(min_length=3, max_length=254, pattern=r'^[^ @]+@[^ @]+\.[^ @]+$')
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=12, max_length=128)


class NewUser(AccountInput):
    role: Literal['admin','analyst']


class SetupInput(AccountInput):
    confirm_password: str = Field(min_length=12, max_length=128)


@app.get('/api/setup')
def setup_status():
    return {'required': not bool(db.rows('SELECT 1 FROM users LIMIT 1'))}


@app.post('/api/setup', status_code=201)
def setup(data: SetupInput):
    if not data.display_name.strip():
        raise HTTPException(422, 'Enter a display name.')
    if data.password != data.confirm_password:
        raise HTTPException(422, 'Passwords do not match.')
    password_hash = security.hash_password(data.password)
    with db.connect() as conn:
        # Serialize first-account creation across concurrent requests/workers.
        conn.execute('SELECT pg_advisory_xact_lock(7462302)')
        if conn.execute('SELECT 1 FROM users LIMIT 1').fetchone():
            raise HTTPException(409, 'Setup is already complete. Sign in with your existing account.')
        conn.execute("INSERT INTO users(email,display_name,password_hash,role) VALUES (%s,%s,%s,'admin')",
                     (data.email.lower(), data.display_name.strip(), password_hash))
    return {'message': 'Administrator account created. Sign in to continue.'}


@app.get('/api/health')
def health():
    db.rows('SELECT 1')
    return {'status': 'ok', 'database': 'PostgreSQL'}


@app.post('/api/login')
def login(data: Login, request: Request, response: Response):
    key = request.client.host if request.client else 'local'
    with attempt_lock:
        now = time.monotonic()
        # Bound memory and expire idle entries; one worker is intentional.
        for old in list(attempts):
            while attempts[old] and attempts[old][0] < now-300:
                attempts[old].popleft()
            if not attempts[old]:
                del attempts[old]
        if len(attempts[key]) >= 10:
            raise HTTPException(429, 'Too many sign-in attempts. Try again in five minutes.')
        attempts[key].append(now)
    users = db.rows('SELECT * FROM users WHERE email=%s', (data.email.strip().lower(),))
    stored = users[0]['password_hash'] if users else DUMMY_HASH
    valid = security.verify_password(data.password, stored)
    if not users or not valid:
        raise HTTPException(401, 'Invalid email or password.')
    token = secrets.token_urlsafe(32)
    with db.connect() as conn:
        conn.execute('DELETE FROM sessions WHERE expires_at<=now()')
        conn.execute('DELETE FROM sessions WHERE token_hash=%s', (security.token_hash(request.cookies.get(COOKIE,'')),))
        conn.execute("INSERT INTO sessions VALUES (%s,%s,now()+interval '8 hours')", (security.token_hash(token), users[0]['user_id']))
    response.set_cookie(COOKIE, token, httponly=True, secure=os.environ.get('COOKIE_SECURE','false').lower()=='true',
                        samesite='strict', max_age=28800, path='/')
    return {k:users[0][k] for k in ('user_id','email','display_name','role')}


@app.post('/api/logout')
def logout(request: Request, response: Response):
    with db.connect() as conn:
        conn.execute('DELETE FROM sessions WHERE token_hash=%s', (security.token_hash(request.cookies.get(COOKIE,'')),))
    response.delete_cookie(COOKIE, path='/')
    return {'ok': True}


@app.get('/api/me')
def me(user=Depends(current_user)):
    return user


@app.get('/api/catalog')
def catalog(user=Depends(current_user)):
    return {'companies': db.rows('SELECT * FROM companies ORDER BY company_name'),
            'models': db.rows('SELECT * FROM models ORDER BY model_id')}


@app.get('/api/memories')
def memories(sector: str | None=None, decision: Literal['BUY','SELL','HOLD'] | None=None,
             user=Depends(current_user)):
    return db.rows('SELECT * FROM memory_details WHERE (%s::text IS NULL OR sector=%s) AND (%s::text IS NULL OR decision=%s) ORDER BY reasoning_id DESC',
                   (sector, sector, decision, decision))


@app.post('/api/memories', status_code=201)
def create_memory(data: MemoryInput, user=Depends(current_user)):
    if data.company_id is None and not all((data.company_name, data.ticker, data.sector)):
        raise HTTPException(422, 'A new company requires a name, ticker and sector.')
    with db.connect(user['user_id']) as conn:
        company_id = data.company_id
        if company_id is None:
            company_id = conn.execute('INSERT INTO companies(company_name,ticker,sector) VALUES (%s,%s,%s) RETURNING company_id',
                                      (data.company_name,data.ticker.upper(),data.sector)).fetchone()['company_id']
        news_id = conn.execute('INSERT INTO news(headline,news_text,published_at) VALUES (%s,%s,%s) RETURNING news_id',
                               (data.headline,data.news_text,data.published_at)).fetchone()['news_id']
        investment_id = conn.execute('''INSERT INTO investments(company_id,model_id,investment_amount,decision,trade_date,return_percentage,created_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING investment_id''',
            (company_id,data.model_id,data.amount,data.decision,data.trade_date,data.return_percentage,user['user_id'])).fetchone()['investment_id']
        rid = conn.execute('INSERT INTO investment_reasoning(investment_id,news_id,reasoning_text,confidence) VALUES (%s,%s,%s,%s) RETURNING reasoning_id',
                            (investment_id,news_id,data.reasoning_text,data.confidence)).fetchone()['reasoning_id']
    # Explicit repair avoids ambiguous save retries and keeps embedding downloads off writes.
    return {'reasoning_id': rid, 'message': 'Saved in PostgreSQL. An administrator can rebuild the semantic index.'}


@app.patch('/api/memories/{reasoning_id}')
def update_outcome(reasoning_id: int, data: Outcome, user=Depends(current_user)):
    with db.connect(user['user_id']) as conn:
        row = conn.execute('SELECT i.* FROM investments i JOIN investment_reasoning r USING(investment_id) WHERE r.reasoning_id=%s FOR UPDATE OF i', (reasoning_id,)).fetchone()
        if not row:
            raise HTTPException(404,'Memory not found.')
        if user['role'] != 'admin' and row['created_by'] != user['user_id']:
            raise HTTPException(403,'You may update only your own outcomes.')
        if row['revision'] != data.revision:
            raise HTTPException(409,'This memory changed. Refresh before saving.')
        conn.execute('UPDATE investments SET return_percentage=%s,revision=revision+1 WHERE investment_id=%s',
                     (data.return_percentage,row['investment_id']))
    return {'message': 'Outcome updated and audit recorded.'}


@app.delete('/api/memories/{reasoning_id}')
def delete_memory(reasoning_id: int, user=Depends(admin)):
    with db.connect(user['user_id']) as conn:
        row = conn.execute('SELECT * FROM investment_reasoning WHERE reasoning_id=%s FOR UPDATE', (reasoning_id,)).fetchone()
        if not row:
            raise HTTPException(404,'Memory not found.')
        conn.execute('DELETE FROM investment_reasoning WHERE reasoning_id=%s', (reasoning_id,))
        conn.execute('DELETE FROM investments WHERE investment_id=%s AND NOT EXISTS (SELECT 1 FROM investment_reasoning WHERE investment_id=%s)',
                     (row['investment_id'],row['investment_id']))
        conn.execute('DELETE FROM news WHERE news_id=%s AND NOT EXISTS (SELECT 1 FROM investment_reasoning WHERE news_id=%s)', (row['news_id'],row['news_id']))
    return {'message': 'Memory deleted. Search excludes it immediately; rebuild removes its cached vector.'}


@app.get('/api/reports')
def reports(user=Depends(current_user)):
    queries = [q.strip() for q in (db.ROOT/'sql/05_reports.sql').read_text().split(';') if q.strip()]
    queries += ["SELECT sector, COUNT(*) AS investment_count, ROUND(AVG(return_percentage),2) AS average_return FROM memory_details GROUP BY sector HAVING COUNT(*)>=2 ORDER BY average_return DESC",
                'SELECT company_name,decision,return_percentage FROM memory_details WHERE return_percentage>(SELECT AVG(return_percentage) FROM investments) ORDER BY return_percentage DESC']
    titles = ['Average return by company','Investments by sector','Top five outcomes','Return by model','Sectors with multiple memories','Above-average outcomes']
    return [{'title':title,'sql':query,'rows':db.rows(query)} for title,query in zip(titles,queries)]


@app.get('/api/search')
def search(q: str=Query(min_length=1,max_length=2000), sector: str | None=None,
           decision: Literal['BUY','SELL','HOLD'] | None=None, user=Depends(current_user)):
    if not q.strip():
        raise HTTPException(422,'Enter a search idea.')
    try:
        return vectors.search(q.strip(),sector,decision)
    except Exception:
        logging.exception('Semantic search failed')
        raise HTTPException(503,'Semantic index unavailable. Ask an administrator to rebuild it.')


@app.get('/api/index')
def index_status(user=Depends(current_user)):
    try:
        return vectors.status()
    except Exception:
        raise HTTPException(503,'Chroma is unavailable. Check backend dependencies and storage.')


@app.post('/api/index/rebuild')
def rebuild_index(user=Depends(admin)):
    try:
        return {'indexed':vectors.rebuild()}
    except Exception:
        logging.exception('Index rebuild failed')
        raise HTTPException(503,'Index rebuild failed. PostgreSQL records are preserved; check model availability and retry.')


@app.get('/api/audit')
def audit(user=Depends(admin)):
    return db.rows('SELECT a.*,u.display_name AS actor FROM audit_log a LEFT JOIN users u ON a.actor_id=u.user_id ORDER BY audit_id DESC LIMIT 100')


@app.post('/api/users', status_code=201)
def create_user(data: NewUser, user=Depends(admin)):
    with db.connect() as conn:
        result = conn.execute('INSERT INTO users(email,display_name,password_hash,role) VALUES (%s,%s,%s,%s) RETURNING user_id,email,display_name,role',
                              (data.email.lower(),data.display_name.strip(),security.hash_password(data.password),data.role)).fetchone()
    return result
