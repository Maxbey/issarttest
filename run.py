import sys

from eve import Eve
from eve.auth import requires_auth
from gevent import monkey, wsgi

from handlers import WAVInfoHandler, MP3ToWAVHandler
from auth import UARAuth

monkey.patch_all()
app = Eve(auth=UARAuth)


@app.route('/wav-info/<string:wav_key>')
@requires_auth('wav-info')
def get_wav_info(wav_key):
    return WAVInfoHandler.get(wav_key)


@app.route('/mp3-to-wav/<string:mp3_key>', methods=['POST'])
@requires_auth('mp3-to-wav')
def post_mp3_to_wav(mp3_key):
    return MP3ToWAVHandler.post(mp3_key)


if __name__ == '__main__':
    port = 8080 if len(sys.argv) != 2 else int(sys.argv[1])
    ws = wsgi.WSGIServer(('localhost', port), app)
    ws.serve_forever()
