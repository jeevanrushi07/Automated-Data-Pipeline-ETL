import os
from typing import Iterable

import psycopg2
from psycopg2.extras import execute_values

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS github_repositories (
    github_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    full_name TEXT NOT NULL UNIQUE,
    owner_login TEXT,
    html_url TEXT,
    description TEXT,
    language TEXT,
    stars INTEGER NOT NULL DEFAULT 0,
    forks INTEGER NOT NULL DEFAULT 0,
    open_issues INTEGER NOT NULL DEFAULT 0,
    watchers INTEGER NOT NULL DEFAULT 0,
    default_branch TEXT,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    pushed_at TIMESTAMPTZ,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

UPSERT_SQL = """
INSERT INTO github_repositories (
    github_id, name, full_name, owner_login, html_url, description, language,
    stars, forks, open_issues, watchers, default_branch, is_archived,
    created_at, updated_at, pushed_at
) VALUES %s
ON CONFLICT (github_id) DO UPDATE SET
    name = EXCLUDED.name,
    full_name = EXCLUDED.full_name,
    owner_login = EXCLUDED.owner_login,
    html_url = EXCLUDED.html_url,
    description = EXCLUDED.description,
    language = EXCLUDED.language,
    stars = EXCLUDED.stars,
    forks = EXCLUDED.forks,
    open_issues = EXCLUDED.open_issues,
    watchers = EXCLUDED.watchers,
    default_branch = EXCLUDED.default_branch,
    is_archived = EXCLUDED.is_archived,
    created_at = EXCLUDED.created_at,
    updated_at = EXCLUDED.updated_at,
    pushed_at = EXCLUDED.pushed_at,
    loaded_at = NOW();
"""


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "github_etl"),
        user=os.getenv("POSTGRES_USER", "airflow"),
        password=os.getenv("POSTGRES_PASSWORD", "airflow"),
    )


def load_records(records: Iterable[dict]) -> int:
    rows = [
        (
            r["github_id"], r["name"], r["full_name"], r["owner_login"], r["html_url"],
            r["description"], r["language"], r["stars"], r["forks"], r["open_issues"],
            r["watchers"], r["default_branch"], r["is_archived"], r["created_at"],
            r["updated_at"], r["pushed_at"],
        )
        for r in records
    ]
    if not rows:
        return 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            execute_values(cur, UPSERT_SQL, rows)
        conn.commit()
    return len(rows)
