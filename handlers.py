import os

from uuid import uuid4

from cerberus import Validator
from flask import jsonify, request
from pydub import AudioSegment

from s3_client import S3Client


class WAVInfoHandler:
    @classmethod
    def get(cls, wav_key):
        tmp_name = S3Client().download_file(wav_key)

        if not tmp_name:
            return jsonify({'error': 'File is missing.'}), 404

        wav = AudioSegment.from_wav(tmp_name)

        return jsonify({
                'channels_count': wav.channels,
                'sample_rate': wav.frame_rate,
                'execution_time': wav.duration_seconds
            })


class MP3ToWAVHandler:
    storage_path = '/tmp/%s'

    @classmethod
    def post(self, mp3_key):
        validator = Validator()
        validation_schema = {
            'wav_target_key': {'type': 'string', 'required': True}
        }

        if not validator.validate(request.json or {} , validation_schema):
            return jsonify(validator.errors), 400

        client = S3Client()

        mp3_tmp = client.download_file(mp3_key)
        if not mp3_tmp:
            return jsonify({'error': 'File is missing.'}), 404

        mp3 = AudioSegment.from_mp3(mp3_tmp)

        wav_tmp = self.storage_path % uuid4().hex
        mp3.export(wav_tmp, format="wav")
        wav = AudioSegment.from_wav(wav_tmp)

        client.upload_file(wav_tmp, request.json.get('wav_target_key'))

        return jsonify({
            'file_size': os.path.getsize(wav_tmp),
            'execution_time': wav.duration_seconds
        }), 201
