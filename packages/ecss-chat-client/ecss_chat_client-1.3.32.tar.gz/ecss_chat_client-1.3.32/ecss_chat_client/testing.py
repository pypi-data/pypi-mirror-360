from urllib.request import Request

from .lib import Base


class Testing(Base):
    def new_user(
            self,
            username,
            name: str,
            password: str,
            domain: str,
    ) -> Request:
        response = self._make_request(
            'testing.newUser',
            payload={
                'username': username,
                'name': name,
                'password': password,
                'domain': domain,
            },
        )
        return response
