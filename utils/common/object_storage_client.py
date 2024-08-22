import os
from io import BytesIO

import boto3
import pandas as pd

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


def load_csv_from_s3(object_storage_key: str, sep: str = ";"):
    downloaded_file = download_file(settings.SCW_S3_BUCKET, object_storage_key)

    # Convert the downloaded bytes to a BytesIO object
    file_content = BytesIO(downloaded_file)

    # List of common encodings to try

    # Try reading the file with each encoding until one works
    file_content.seek(0)  # Reset the buffer position to the beginning
    df = pd.read_csv(file_content, sep=sep, encoding="utf-8", index_col=False)

    return df


def download_folder(bucket_name: str, folder_name: str, local_dir: str):
    """
    Télécharge tous les fichiers d'un dossier S3 vers un répertoire local.

    :param bucket_name: Le nom du bucket S3.
    :param folder_name: Le nom du dossier dans le bucket S3.
    :param local_dir: Le répertoire local où les fichiers doivent être sauvegardés.
    """
    paginator = s3_client.get_paginator("list_objects_v2")
    result_iterator = paginator.paginate(Bucket=bucket_name, Prefix=folder_name)

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    for page in result_iterator:
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                # Extrait le chemin du fichier relatif à folder_name
                relative_path = os.path.relpath(key, folder_name)
                local_file_path = os.path.join(local_dir, relative_path)

                if not os.path.exists(os.path.dirname(local_file_path)):
                    os.makedirs(os.path.dirname(local_file_path))

                # Télécharge le fichier et l'enregistre localement
                with open(local_file_path, "wb") as f:
                    f.write(download_file(bucket_name, key))


def make_folder_public(bucket_name: str, folder_name: str):
    """
    Change la visibilité de tous les objets d'un dossier S3, y compris ceux dans les sous-dossiers, pour les rendre publics.

    :param bucket_name: Le nom du bucket S3.
    :param folder_name: Le nom du dossier dans le bucket S3.
    """
    paginator = s3_client.get_paginator("list_objects_v2")
    result_iterator = paginator.paginate(Bucket=bucket_name, Prefix=folder_name)

    for page in result_iterator:
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                # Change la visibilité de chaque objet à public-read
                s3_client.put_object_acl(Bucket=bucket_name, Key=key, ACL="public-read")
