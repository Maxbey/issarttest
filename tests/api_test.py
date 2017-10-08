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


class WAVInfoAPITest(EveTestCase):
    url = '/wav-info/%s'

    def test_attempt_to_access_without_header(self):
        response = self.app.get(self.url % 'key')

        self.assertEquals(response.status_code, 401)

    def test_attempt_to_access_invalid_header(self):
        response = self.app.get(
            self.url % 'key',
            headers={'Authorization': 'something'}
        )

        self.assertEquals(response.status_code, 401)

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


class MP3ToWAVAPITest(EveTestCase):
    url = '/mp3-to-wav/%s'

    def test_attempt_to_access_without_header(self):
        response = self.app.post(self.url % 'key')

        self.assertEquals(response.status_code, 401)

    def test_attempt_to_access_invalid_header(self):
        response = self.app.post(
            self.url % 'key',
            headers={'Authorization': 'something'}
        )

        self.assertEquals(response.status_code, 401)

    def test_empty_payload(self):
        response = self.app.post(
            self.url % 'key',
            **self.auth_header
        )

        self.assertEquals(response.status_code, 400)
        self.assertEquals(
            self.deserialize(response.data),
            {'wav_target_key': 'required field'}
        )

    def test_file_not_found(self):
        self.s3_client_mock.download_file.return_value = None
        mp3_key = 'mp3'

        response = self.app.post(
            self.url % mp3_key,
            data=json.dumps({'wav_target_key': 'key'}),
            content_type='application/json',
            **self.auth_header
        )

        self.s3_client_mock.download_file.assert_called_once_with(mp3_key)
        self.assertEquals(response.status_code, 404)
        self.assertEquals(
            {'error': 'File is missing.'},
            self.deserialize(response.data)
        )

    @patch('handlers.os.path.getsize')
    @patch('handlers.uuid4')
    def test_conversion(self, uuid4_mock, getsize):
        mp3 = Mock()
        wav = Mock(duration_seconds=3.33)
        mp3_key = 'mp3'
        uuid4_mock.return_value = Mock(hex='wav_tmp')
        getsize.return_value = 123
        self.s3_client_mock.download_file.return_value = 'mp3_tmp'
        self.audio_segment_mock.from_mp3.return_value = mp3
        self.audio_segment_mock.from_wav.return_value = wav

        expected_response = {
            'file_size': getsize.return_value,
            'execution_time': wav.duration_seconds

        }

        response = self.app.post(
            self.url % mp3_key,
            data=json.dumps({'wav_target_key': 'target_key'}),
            content_type='application/json',
            **self.auth_header
        )

        self.s3_client_mock.download_file.assert_called_once_with(mp3_key)
        self.audio_segment_mock.from_mp3.assert_called_once_with('mp3_tmp')
        mp3.export.assert_called_once_with('/tmp/wav_tmp', format='wav')
        self.s3_client_mock.upload_file.assert_called_once_with(
            '/tmp/wav_tmp', 'target_key'
        )

        self.assertEquals(response.status_code, 201)
        self.assertEquals(self.deserialize(response.data), expected_response)
