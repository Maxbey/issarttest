#### Simple HTTP listener written on Eve framework.
--------------
#### Requirements
+ python 3
+ ffmpeg

#### Installation and usage
Run `make install` to install dependencies and `python3 run.py` to start listener.
Also, you can specify the port for listener via `python3 run.py 9000`


#### Available endpoints

Method | Url | Payload
------------ | ------------ | ------------
GET | `/wav-info/<wav_key>`/ | -
POST | `/mp3-to-wav/<mp3_key>`/ | `{"wav_target_key": "string"}`

#### Testing
Run `make devinstall` to install dependencies for testing and run tests by `make test`
