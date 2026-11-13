import argparse
from getpass import getpass
from . import db, security, vectors


def main():
    parser = argparse.ArgumentParser(description='Initialize PostgreSQL, create an account, or rebuild Chroma.')
    parser.add_argument('command', choices=['init','create-user','rebuild-index'])
    parser.add_argument('--email')
    parser.add_argument('--name')
    parser.add_argument('--role',choices=['admin','analyst'],default='admin')
    args = parser.parse_args()
    if args.command == 'init':
        db.initialize()
        print('PostgreSQL schema and synthetic seed data ready.')
    elif args.command == 'rebuild-index':
        print('Indexed memories:', vectors.rebuild())
    else:
        if not args.email or not args.name:
            parser.error('create-user requires --email and --name')
        password = getpass('New password (12-128 characters): ')
        if password != getpass('Repeat password: '):
            parser.error('Passwords do not match.')
        try:
            password_hash = security.hash_password(password)
        except ValueError as exc:
            parser.error(str(exc))
        with db.connect() as conn:
            conn.execute('INSERT INTO users(email,display_name,password_hash,role) VALUES (%s,%s,%s,%s)',
                         (args.email.strip().lower(),args.name.strip(),password_hash,args.role))
        print('Account created.')


if __name__ == '__main__':
    main()
