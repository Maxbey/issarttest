import json
import unittest
from mock import patch, Mock

from run import app


class EveTestCase(unittest.TestCase):
    @property
    def auth_header(self):
        return {'headers': {'Authorization': 'UAR-2017'}}

    def setUp(self):
        self.app = app.test_client()

        self.s3_client_class_patch = patch('handlers.S3Client')
        self.s3_client_class_mock = self.s3_client_class_patch.start()
        self.s3_client_mock = Mock()
        self.s3_client_class_mock.return_value = self.s3_client_mock

        self.audio_segment_patch = patch('handlers.AudioSegment')
        self.audio_segment_mock = self.audio_segment_patch.start()

    def tearDown(self):
        self.s3_client_class_patch.stop()
        self.audio_segment_patch.stop()

    def deserialize(self, response_data):
        return json.loads(str(response_data, 'utf-8'))


class AuthTestMixin:
    def test_attempt_to_access_without_header(self):
        response = self.app.get(self.url % 'key')

        self.assertEquals(response.status_code, 401)

    def test_attempt_to_access_invalid_header(self):
        response = self.app.get(
            self.url % 'key',
            headers = {'Authorization': 'something'}
        )

        self.assertEquals(response.status_code, 401)


class WAVInfoAPITest(AuthTestMixin, EveTestCase):
    url = '/wav-info/%s'

    def test_file_not_found(self):
        self.s3_client_mock.download_file.return_value = None
        wav_key = 'wav'

        response = self.app.get(
            self.url % wav_key,
            **self.auth_header
        )

        self.s3_client_mock.download_file.assert_called_once_with(wav_key)
        self.assertEquals(response.status_code, 404)
        self.assertEquals(
            {'error': 'File is missing.'},
            self.deserialize(response.data)
        )

    def test_wav_info_retrieving(self):
        self.audio_segment_mock.from_wav.return_value = Mock(
            channels=2, frame_rate=44100, duration_seconds=2.78
        )
        expected_info = {
            'channels_count': 2,
            'sample_rate': 44100,
            'execution_time': 2.78
        }
        wav_key = 'wav'

        response = self.app.get(
            self.url % wav_key,
            **self.auth_header
        )
        self.audio_segment_mock.from_wav.assert_called_once_with(
            self.s3_client_mock.download_file.return_value
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(expected_info, self.deserialize(response.data))
