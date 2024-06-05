import boto3

from utils.core.settings import settings

boto3_session = boto3.session.Session()

s3_client = boto3_session.client(
    service_name="s3",
    region_name=settings.SCW_S3_REGION,
    use_ssl=True,
    endpoint_url=settings.SCW_S3_URL,
    aws_access_key_id=settings.SCW_ACCESS_KEY,
    aws_secret_access_key=settings.SCW_SECRET_KEY,
)


def upload_file(bucket_name: str, key: str, body: str | bytes, acl: str = "private"):
    s3_client.put_object(Bucket=bucket_name, Key=key, Body=body, ACL=acl)


def download_file(bucket_name: str, key: str):
    return s3_client.get_object(Bucket=bucket_name, Key=key)["Body"].read()
