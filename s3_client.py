import boto3

from botocore.handlers import disable_signing
from botocore.exceptions import ClientError
from uuid import uuid4


class S3Client:
    s3_bucket = 'isstestbucket'

    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.s3.meta.client.meta.events.register(
            'choose-signer.s3.*',
            disable_signing
        )

    def download_file(self, file_name):
        tmp_file = uuid4().hex
        try:
            self.s3.Bucket(self.s3_bucket).download_file(
                file_name, tmp_file
            )
        except ClientError:
            return None

        return tmp_file

    def upload_file(self, path, target_name):
        self.s3.Bucket(self.s3_bucket).upload_file(
            path, target_name
        )

        object_acl = self.s3.ObjectAcl(self.s3_bucket, target_name)
        object_acl.put(ACL='public-read')
