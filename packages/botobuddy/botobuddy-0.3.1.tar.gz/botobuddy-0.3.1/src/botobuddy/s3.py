import click
import logging as lg
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from boto3.s3.transfer import TransferConfig
from types_boto3_s3 import S3Client

from botobuddy.common import get_s3_client


class S3Uri:
    def __init__(self, s3_uri: str):
        self.s3_uri = s3_uri
        self.parsed_uri = urlparse(s3_uri)
        self.bucket = self.parsed_uri.netloc
        self.path = self.parsed_uri.path.lstrip('/')
        self.filename = self.parsed_uri.path.split('/')[-1]
        self.parent_uri = 's3://' + self.bucket + '/' + '/'.join(self.path.split('/')[:-1])

    def __str__(self):
        return self.s3_uri


def import_commands(parent):
    parent.add_command(s3_group)


@click.group(name='s3')
def s3_group():
    pass


@s3_group.command(name='delete-bucket')
@click.argument('bucket_name')
@click.pass_obj
def delete_bucket_cmd(obj, bucket_name):
    '''Clean and delete an S3 bucket completely'''
    try:
        client = get_s3_client(obj)

        # First empty the bucket
        delete_bucket_contents(client, bucket_name)

        # Then delete the bucket itself
        delete_bucket(client, bucket_name)

    except Exception as e:
        raise UserWarning(f'Error deleting bucket {bucket_name} {e}') from e


@s3_group.command(name='ls')
@click.argument('s3_path')
@click.pass_obj
def ls_cmd(obj, s3_path):
    client = get_s3_client(obj)

    def print_object(item):
        lg.info(item['Key'])  # type: ignore

    list_all_objects(client, s3_path, print_object)


def list_all_objects(client: S3Client, s3_path: str | S3Uri, on_object):
    '''List all objects in an S3 bucket and call on_object for each'''
    if isinstance(s3_path, str):
        s3_uri = S3Uri(s3_path)
    else:
        s3_uri = s3_path

    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=s3_uri.bucket, Prefix=s3_uri.path)

    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                on_object(obj)


def delete_bucket_contents(client, bucket_name):
    '''
    Deletes all objects and object versions from the specified S3 bucket
    '''
    lg.info(f'Deleting all objects in bucket: {bucket_name}')

    # Delete all objects and their versions
    paginator = client.get_paginator('list_object_versions')
    page_iterator = paginator.paginate(Bucket=bucket_name)

    for page in page_iterator:
        # Delete object versions if they exist
        if 'Versions' in page:
            for version in page['Versions']:
                client.delete_object(
                    Bucket=bucket_name,
                    Key=version['Key'],
                    VersionId=version['VersionId']
                )
                lg.info(f'Deleted object: {version["Key"]} (version {version["VersionId"]})')

        # Delete delete markers if they exist
        if 'DeleteMarkers' in page:
            for marker in page['DeleteMarkers']:
                client.delete_object(
                    Bucket=bucket_name,
                    Key=marker['Key'],
                    VersionId=marker['VersionId']
                )
                lg.info(f'Deleted delete marker: {marker["Key"]} (version {marker["VersionId"]})')

    # Delete objects in a non-versioned bucket
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name)

    objects_to_delete = []
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                objects_to_delete.append({'Key': obj['Key']})

            if objects_to_delete:
                # Delete in batches of 1000 (AWS limit)
                for i in range(0, len(objects_to_delete), 1000):
                    batch = objects_to_delete[i:i+1000]

                    client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': batch}
                    )

                    lg.info(f'Deleted {len(batch)} objects')

                objects_to_delete = []


def delete_bucket(client, bucket_name):
    '''
    Deletes the specified S3 bucket after emptying it
    '''

    # Delete the bucket
    lg.info(f'Deleting bucket: {bucket_name}')
    client.delete_bucket(Bucket=bucket_name)
    lg.info(f'Bucket {bucket_name} has been deleted successfully')


def fast_download_s3_files(
    targets: list[tuple[str, str, str | Path]],
    skip_existing: bool = False,
    create_folders: bool = True,
    concurrency: int = 100,
    session_config: dict = {}
):
    '''Download a list of files from S3 in parallel.

    Args:
        targets: List of tuples containing (bucket, key, local_path)
        skip_existing: Skip files that already exist locally
        create_folders: Create the folders for the files
        concurrency: Number of concurrent downloads
        session_config: Configuration for the AWS session (profile, region, etc.)
    '''

    boto_config = {
        'max_pool_connections': int(1.5 * concurrency)
    }

    client = get_s3_client(session_config, core_config=boto_config)

    config = {
        'transfer_config': TransferConfig(
            use_threads=False
        )
    }

    lg.info(f'Downloading {len(targets)} files')

    if create_folders:
        folders = set()

        for target in targets:
            folders.add(Path(target[2]).parent)

        for folder in folders:
            lg.info(f'Creating folder {folder}')
            folder.mkdir(parents=True, exist_ok=True)

    def download_file(bucket_name, key, local_path):
        if isinstance(local_path, Path):
            local_path = str(local_path)

        if skip_existing and Path(local_path).exists():
            return f'Skipping {key} because it already exists'

        client.download_file(
            bucket_name, key, local_path,
            Config=config['transfer_config']
        )

        return f'Successfully downloaded {key}'

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(
                download_file,
                target[0],
                target[1],
                target[2],
            ) for target in targets
        ]

        for future in futures:
            lg.debug(future.result())
