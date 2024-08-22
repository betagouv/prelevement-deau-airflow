import datetime

from airflow import DAG

from utils.public_bucket_acl.tasks import PublicBucketACLOperator

with DAG(
    dag_id="dag_public_bucket_acl",
    start_date=datetime.datetime(2024, 4, 24, hour=1),
    schedule="@hourly",
    catchup=False,
):
    PublicBucketACLOperator(task_id="set_public_bucket_acl")
