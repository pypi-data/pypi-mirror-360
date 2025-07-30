from http import HTTPStatus

import requests

from .scheme import AuthResponse


class AuthenticationError(Exception):
    """Исключение для ошибок аутентификации."""


def auth(
    *args,
):
    username, password, server, proto, port, verify = args
    url = f'{proto}://{server}:{port}/api/v1/login'
    login_data = {
        'user': username,
        'password': password,
    }
    if proto == 'http':
        response = requests.post(
                url,
                json=login_data,
            )
    if proto == 'https':
        response = requests.post(
            url,
            json=login_data,
            verify=verify,
        )
    if response.status_code != HTTPStatus.OK:
        raise AuthenticationError('Maybe?- SYSTEM_ADMIN_PASSWORD=password')
    auth_response = AuthResponse(**response.json())
    token = auth_response.data.authToken
    uid = auth_response.data.me.id
    return token, uid


class Auth:

    @staticmethod
    def session(*args):
        auth_token, uid = auth(*args)
        session = requests.Session()
        headers = {
            'X-Auth-Token': auth_token,
            'X-User-Id': uid,
        }
        session.headers.update(headers)
        session.cookies.set('rc_token', auth_token)
        session.cookies.set('rc_uid', uid)
        session.username = args[0]
        session.uid = uid
        return session
