"""Start an optional workspace-local PostgreSQL server from official EDB binaries.

Extract pgsql/bin, pgsql/lib and pgsql/share into .deps first. Does not install a
Windows service. Generated credentials stay in ignored data/ and .env files.
"""
import os
import secrets
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / '.deps/pgsql/bin'
DATA = ROOT / 'data/postgres'


def main():
    if not (BIN/'initdb.exe').exists():
        raise SystemExit('Extract official PostgreSQL Windows binaries into .deps/pgsql first.')
    if not DATA.exists():
        if (ROOT/'.env').exists():
            raise SystemExit('Existing .env found. Use the configured server, or move it aside before local bootstrap.')
        DATA.parent.mkdir(exist_ok=True)
        password=secrets.token_urlsafe(32)
        pwfile=ROOT/'data/.pg-init-password'
        pwfile.write_text(password,encoding='utf-8')
        try:
            subprocess.run([str(BIN/'initdb.exe'),'-D',str(DATA),'-U','ime_owner','-A','scram-sha-256',
                            '--pwfile',str(pwfile),'--encoding=UTF8','--locale=C'],check=True)
        finally:
            pwfile.unlink(missing_ok=True)
        with (DATA/'postgresql.conf').open('a') as file:
            file.write("\nlisten_addresses = '127.0.0.1'\nport = 55432\n")
        (ROOT/'.env').write_text(f'DATABASE_URL=postgresql://ime_owner:{password}@127.0.0.1:55432/investment_memory\nAPP_ORIGIN=http://localhost:3000\nCOOKIE_SECURE=false\nCHROMA_PATH=./data/chroma_v2\n',encoding='utf-8')
    status=subprocess.run([str(BIN/'pg_ctl.exe'),'-D',str(DATA),'status'],capture_output=True)
    if status.returncode:
        subprocess.run([str(BIN/'pg_ctl.exe'),'-D',str(DATA),'-l',str(ROOT/'data/postgres.log'),'-w','start'],check=True)
    from dotenv import load_dotenv
    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    load_dotenv(ROOT/'.env')
    settings=conninfo_to_dict(os.environ['DATABASE_URL'])
    settings['dbname']='postgres'
    with psycopg.connect(make_conninfo(**settings),autocommit=True) as conn:
        if not conn.execute("SELECT 1 FROM pg_database WHERE datname='investment_memory'").fetchone():
            conn.execute('CREATE DATABASE investment_memory')
    print('Local PostgreSQL ready on 127.0.0.1:55432. Credentials are in ignored .env.')


if __name__=='__main__':
    main()
