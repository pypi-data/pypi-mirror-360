from .lib import Base


class Users(Base):
    def info(self, username: str):
        return self._make_request(
            'users.info', params={'username': username}, method='get',
        )

    def search_for_room_mention(
            self,
            room_id: str,
            query: str = '',
            members_only: int = 1,
    ):
        return self._make_request(
            'users.searchForRoomMention',
            params={
                'roomId': room_id,
                'query': query,
                'count': self.settings.count,
                'offset': self.settings.offset,
                'searchInMembersOnly': members_only,
            },
            method='get',
        )

    def me(self):
        return self._make_request(
            'me', method='get',
        )
