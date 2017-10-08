import unittest

from botocore.exceptions import ClientError
from mock import Mock, patch

from s3_client import S3Client


class EveTestCase(unittest.TestCase):
    def setUp(self):
        self.s3_bucket = Mock()
        self.hex = 'hex'

        self.client = S3Client()
        self.client.s3 = Mock()
        self.client.s3.Bucket.return_value = self.s3_bucket

        self.uuid_patch = patch('s3_client.uuid4')
        self.uuid_mock = self.uuid_patch.start()
        self.uuid_mock.return_value = Mock(hex=self.hex)

    def tearDown(self):
        self.uuid_patch.stop()

    def test_attempt_to_download_non_existed(self):
        self.s3_bucket.download_file.side_effect = ClientError({}, 'name')
        self.assertIsNone(self.client.download_file('file'))

        self.s3_bucket.download_file.assert_called_once_with(
            'file', '/tmp/%s' % self.hex
        )

    def test_successful_download(self):
        self.assertEquals(
            '/tmp/%s' % self.hex, self.client.download_file('file')
        )
        self.s3_bucket.download_file.assert_called_once_with(
            'file', '/tmp/%s' % self.hex
        )

    def test_successful_upload(self):
        path = 'path'
        target = 'target'

        self.client.upload_file(path, target)
        self.s3_bucket.upload_file.assert_called_once_with(
            path, target
        )
