from types import NoneType
import jwt
import secretsHandler
import time

class AMToken:
    last: str|NoneType = None

    def generate():
        key_id = secretsHandler.key_id()
        team_id = secretsHandler.team_id()

        if None in [key_id,team_id]:
            print([key_id,team_id])
            return None

        auth_key = secretsHandler.secret_key

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