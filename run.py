import sys

from eve import Eve
from handlers import WAVInfoHandler

app = Eve()


@app.route('/wav-info/<string:wav_key>')
def get_wav_info(wav_key):
    return WAVInfoHandler.get(wav_key)


@app.route('/mp3-to-wav/<string:mp3_key>', methods=['POST'])
def post_mp3_to_wav(mp3_key):
    pass


if __name__ == '__main__':
    port = 8080 if len(sys.argv) != 2 else int(sys.argv[1])
    app.run(port=port)
