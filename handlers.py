from flask import jsonify
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
