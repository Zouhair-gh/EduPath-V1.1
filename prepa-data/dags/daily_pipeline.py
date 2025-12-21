from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


def trigger_prepa_data_pipeline():
    import urllib.request
    url = "http://prepa-data-api:8001/api/pipeline/trigger"
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode("utf-8"))


default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'daily_prepa_data_pipeline',
    default_args=default_args,
    schedule_interval='0 2 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

run = PythonOperator(
    task_id='trigger_prepa_data_pipeline',
    python_callable=trigger_prepa_data_pipeline,
    dag=dag
)
