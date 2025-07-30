from .lib import Base


class Avatar(Base):
    def get_avatar(self, user_id: str):
        return self._make_request(
            f'avatar/{user_id}',
            params={
                'etag': 'DEFAULT',
            },
            method='get',
        )

    def get_avatar_user(self, user_id: str):
        return self._make_request(
            f'avatar/user/{user_id}', method='get',
            short_path=True,
        )

    def get_avatar_room(self, room_id: str):
        return self._make_request(
            f'avatar/room/{room_id}', method='get',
            short_path=True,
        )
