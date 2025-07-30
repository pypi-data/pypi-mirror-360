from requests import Request

from .lib import Base


class ApiInfo(Base):

    def swagger_info(self) -> Request:
        return self._make_request(
            endpoint='api',
            api_info=True,
            method='GET',
        )

    def open_api_yaml(self) -> Request:
        return self._make_request(
            endpoint='api-yaml',
            api_info=True,
            method='GET',
        )

    def open_api_json(self) -> Request:
        return self._make_request(
            endpoint='api-json',
            api_info=True,
            method='GET',
        )

    def static_recourse(self, endpoint: str) -> Request:
        return self._make_request(
            endpoint=endpoint,
            api_info=True,
            method='HEAD',
        )
