# Automated Data Pipeline — GitHub Repository ETL

An end-to-end data engineering project that extracts GitHub repository metadata through the GitHub REST API, transforms and deduplicates the data in Python, and upserts it into PostgreSQL. Apache Airflow orchestrates the pipeline with a daily schedule and retry handling. Docker Compose runs Airflow and PostgreSQL locally.

## Architecture

```text
GitHub REST API
      |
      v
Python Extraction
      |
      v
Transform + Deduplicate
      |
      v
PostgreSQL Upsert
      ^
      |
Apache Airflow (daily + retries)
      ^
      |
Docker Compose
```

## What it does

- Searches repositories for five programming languages: Python, Java, JavaScript, C++, and Go.
- Requests up to 30 repositories per language.
- Uses a GitHub token when supplied to improve API rate limits.
- Deduplicates repositories by GitHub repository ID.
- Loads a target of up to 125 unique records per run.
- Uses PostgreSQL `ON CONFLICT ... DO UPDATE` so reruns update existing repositories instead of creating duplicates.
- Runs the ETL as three Airflow tasks: `extract -> transform -> load`.
- Retries failed tasks up to three times with a five-minute delay.

## Project structure

```text
dags/github_etl_dag.py   # Airflow DAG
src/github_api.py        # GitHub API extraction
src/transform.py         # Cleaning and deduplication
src/database.py          # PostgreSQL table + upsert logic
sql/schema.sql           # Target table definition
config/languages.yaml    # Extraction configuration
tests/test_transform.py  # Basic transformation test
Dockerfile               # Airflow image with project dependencies
docker-compose.yml       # Airflow + PostgreSQL services
.env.example             # Environment variable template
```

## Setup

### 1. Create a GitHub token

Create a GitHub personal access token with only the permissions required for public repository metadata access. Do not commit the real token.

### 2. Configure environment variables

Create `.env` from `.env.example` and put your token in `GITHUB_TOKEN`.

### 3. Start the stack

```bash
docker compose up airflow-init

docker compose up -d airflow-webserver airflow-scheduler
```

Airflow is available at:

`http://localhost:8080`

Login:

- Username: `admin`
- Password: `admin`

### 4. Trigger the DAG

Open the `github_repository_etl` DAG and trigger it manually, or wait for its daily schedule.

### 5. Check the PostgreSQL data

The ETL database is available through the PostgreSQL service on port `5432`.

```bash
psql -h localhost -p 5432 -U airflow -d github_etl
```

Then:

```sql
SELECT COUNT(*) FROM github_repositories;
SELECT language, COUNT(*)
FROM github_repositories
GROUP BY language
ORDER BY COUNT(*) DESC;
```

## Why upserts are used

The pipeline may encounter the same repository on later runs. The GitHub repository ID is the primary key, so `ON CONFLICT (github_id) DO UPDATE` updates the existing row. This makes repeated scheduled runs safe and prevents duplicate rows for the same repository.

## Testing

```bash
python -m pytest
```

## Resume-aligned description

This repository implements the architecture described in the resume project: GitHub API extraction, Python processing, SQL database loading, upserts, token-based authentication, Airflow daily orchestration with retries, and Docker Compose containerization.
