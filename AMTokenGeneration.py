from types import NoneType
import jwt
import secret
import time

class AMToken:
    last: str|NoneType = None

    def generate():
        key_id = secret.key_id
        team_id = secret.team_id
        auth_key_file = secret.secret_key_filename

        with open(auth_key_file, 'r') as f:
            auth_key = f.read()

        header = {
            'alg': 'ES256',
            'kid': key_id,
        }

        payload = {
            'iss': team_id,
            'iat': time.time(),
            'exp': time.time() + 86400 * 179, # 180 days
            # 'aud': 'https://api.music.apple.com',
            # "origin":["https://example.com","https://music.example.com"]
        }

        token = jwt.encode(payload, auth_key, algorithm='ES256', headers=header)
        AMToken.last = token
        return token