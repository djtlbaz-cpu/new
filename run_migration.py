"""
Beat Addicts — One-command Supabase migration runner.

Usage:
    python run_migration.py

You'll be prompted for your database password.
Find it at: Supabase Dashboard → Settings → Database → Connection string
"""
import getpass
import sys

import psycopg2


PROJECT_REF = "izuojgxfpcxnaliocgcd"
REGION = "us-west-2"
MIGRATION_FILE = "supabase_migration.sql"


def get_connection(password: str):
    """Try multiple connection methods."""
    attempts = [
        {
            "label": "Direct connection",
            "host": f"db.{PROJECT_REF}.supabase.co",
            "port": 5432,
            "user": "postgres",
            "password": password,
            "dbname": "postgres",
        },
        {
            "label": "Pooler (session mode)",
            "host": f"aws-0-{REGION}.pooler.supabase.com",
            "port": 5432,
            "user": f"postgres.{PROJECT_REF}",
            "password": password,
            "dbname": "postgres",
        },
        {
            "label": "Pooler (transaction mode)",
            "host": f"aws-0-{REGION}.pooler.supabase.com",
            "port": 6543,
            "user": f"postgres.{PROJECT_REF}",
            "password": password,
            "dbname": "postgres",
        },
    ]

    for attempt in attempts:
        label = attempt.pop("label")
        try:
            conn = psycopg2.connect(**attempt, connect_timeout=10)
            print(f"  Connected via {label}")
            return conn
        except Exception as exc:
            err = str(exc).split("\n")[0]
            print(f"  {label}: {err}")

    return None


def run_migration(conn):
    """Execute the migration SQL file."""
    with open(MIGRATION_FILE, "r", encoding="utf-8") as f:
        sql = f.read()

    conn.autocommit = True
    cur = conn.cursor()

    # Split on semicolons to execute statements individually
    # (needed because CREATE POLICY can't be in a transaction block on some configs)
    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]

    success = 0
    errors = 0
    for stmt in statements:
        # Skip comment-only blocks
        lines = [l for l in stmt.split("\n") if l.strip() and not l.strip().startswith("--")]
        if not lines:
            continue
        try:
            cur.execute(stmt)
            success += 1
        except psycopg2.errors.DuplicateObject:
            # Policy or index already exists — fine
            success += 1
        except Exception as exc:
            err = str(exc).strip().split("\n")[0]
            print(f"  Warning: {err}")
            errors += 1

    cur.close()
    conn.close()
    return success, errors


def verify_tables(password: str):
    """Quick check that tables exist after migration."""
    conn = get_connection(password)
    if not conn:
        return False

    cur = conn.cursor()
    tables = [
        "users", "subscription_tiers", "user_subscriptions",
        "generation_usage", "addons", "user_addons", "content_ownership",
    ]
    all_ok = True
    for table in tables:
        cur.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name=%s)",
            (table,),
        )
        exists = cur.fetchone()[0]
        status = "OK" if exists else "MISSING"
        if not exists:
            all_ok = False
        print(f"  {table}: {status}")

    # Check if tiers were seeded
    cur.execute("SELECT COUNT(*) FROM subscription_tiers")
    tier_count = cur.fetchone()[0]
    print(f"  subscription_tiers rows: {tier_count}")

    cur.execute("SELECT COUNT(*) FROM addons")
    addon_count = cur.fetchone()[0]
    print(f"  addons rows: {addon_count}")

    cur.close()
    conn.close()
    return all_ok


def main():
    print("=" * 60)
    print("Beat Addicts — Supabase Migration Runner")
    print("=" * 60)
    print()
    print(f"Project: {PROJECT_REF}")
    print(f"SQL file: {MIGRATION_FILE}")
    print()
    print("Find your database password at:")
    print("  Supabase Dashboard → Settings → Database")
    print("  (scroll to 'Connection string' → URI tab)")
    print()

    password = getpass.getpass("Enter database password: ")
    if not password:
        print("No password entered. Exiting.")
        sys.exit(1)

    print("\nConnecting...")
    conn = get_connection(password)
    if not conn:
        print("\nFailed to connect. Check your password and try again.")
        sys.exit(1)

    print("\nRunning migration...")
    success, errors = run_migration(conn)
    print(f"\nMigration complete: {success} statements OK, {errors} warnings")

    print("\nVerifying tables...")
    ok = verify_tables(password)
    if ok:
        print("\n✓ All tables created successfully!")
        print("Your subscription system is ready to go.")
    else:
        print("\n✗ Some tables are missing. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
