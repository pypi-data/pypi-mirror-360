from typing import Literal, Optional
from urllib.request import Request

from .lib import Base
from .types import SpotlightSchemas


class Spotlight(Base):
    """Сервис Spotlight."""

    def search_by_spotlight(
            self,
            page_count: int,
            search_query: str,
            search_schema: list[
                SpotlightSchemas.ALL_USERS,
                SpotlightSchemas.UNKNOWN_USERS,
                SpotlightSchemas.DIRECT,
                SpotlightSchemas.PRIVATE,
                SpotlightSchemas.TELECONFERENCE,
                SpotlightSchemas.SUPERGROUP,
                SpotlightSchemas.TOPIC,
                SpotlightSchemas.THREAD_ROOM,
                SpotlightSchemas.GROUPS,
                SpotlightSchemas.MESSAGES,
            ],
    ) -> Request:
        """Поиск spotlight с заданными параметрами.

        Аргументы:
        page_count (int): Количество результатов, которые нужно вернуть.
        search_query (str): строка по которой будет производиться поиск.
        search_schema (list): параметры для фильтрации запроса.

        Возвращает:
        Response: Объект ответа, содержащий результаты поиска.
        """
        return self._make_request(
            'spotlight',
            payload={
                'count': page_count,
                'query': search_query,
                'searchSchema': search_schema,
            },
        )

    def search_spotlight_paginated(
            self,
            query: str,
            sample: Optional[Literal['users', 'rooms']] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
            exception: Optional[str] = None,
    ) -> Request:
        """Поиск spotlight paginated с заданными параметрами.

        Аргументы:
        query (str): строка по которой будет производиться поиск.
        sample (Optional[Literal['users', 'rooms']]): Указывает тип поиска.
        Если указано 'users', будет выполнен поиск пользователей.
        Если указано 'rooms', то будет выполнен поиск по комнатам.
        offset (Optional[int]): Смещение для пагинации.
        count (Optional[int]): Количество результатов, которые нужно вернуть.
        exception (Optional[str]): Фильтрация.
        Например: exception=47, в ответе не будет комнат/юзеров с названием 47.

        Возвращает:
        Response: Объект ответа, содержащий результаты поиска.
        """
        search_type_dict: dict = {'users': '@', 'rooms': '%23'}
        if sample:
            search: str = search_type_dict.get(sample)
            return self._make_request(
                f'spotlight.paginated?offset={offset}&count={count}'
                f'&query={search}{query}&exceptions={exception}',
                method='get',
            )
        return self._make_request(
            f'spotlight.paginated?offset={offset}&count={count}'
            f'&query={sample}{query}&exceptions={exception}',
            method='get',
        )

    def search_spotlight_paginated_broken(
            self,
            url: str,
    ) -> Request:
        """Тестовый эндпоинт без параметров для проверки валидации."""
        return self._make_request(
            url,
            method='get',
        )
