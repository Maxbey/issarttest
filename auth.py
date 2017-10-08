from eve.auth import TokenAuth
from flask import request


class UARAuth(TokenAuth):
    def authorized(self, *args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        return auth_header == 'UAR-2017'
