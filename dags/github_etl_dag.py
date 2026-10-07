import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, "/opt/airflow/src")
from github_api import extract_repositories  # noqa: E402
from transform import transform_records  # noqa: E402
from database import load_records  # noqa: E402


def extract(**context):
    token = os.getenv("GITHUB_TOKEN")
    records = extract_repositories(token=token, per_language=30)
    context["ti"].xcom_push(key="raw_records", value=records)


def transform(**context):
    records = context["ti"].xcom_pull(task_ids="extract", key="raw_records") or []
    transformed = transform_records(records, target=125)
    context["ti"].xcom_push(key="records", value=transformed)


def load(**context):
    records = context["ti"].xcom_pull(task_ids="transform", key="records") or []
    count = load_records(records)
    print(f"Upserted {count} repository records.")



default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="github_repository_etl",
    default_args=default_args,
    description="Daily GitHub repository ETL: API -> transform -> PostgreSQL",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["etl", "github", "postgres", "data-engineering"],
) as dag:
    extract_task = PythonOperator(task_id="extract", python_callable=extract)
    transform_task = PythonOperator(task_id="transform", python_callable=transform)
    load_task = PythonOperator(task_id="load", python_callable=load)

    extract_task >> transform_task >> load_task
