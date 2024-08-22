from airflow.models import BaseOperator

from utils.common.object_storage_client import make_folder_public
from utils.core.settings import settings


class PublicBucketACLOperator(BaseOperator):
    def execute(self, context):
        make_folder_public(settings.SCW_S3_PUBLIC_BUCKET, folder_name="")
