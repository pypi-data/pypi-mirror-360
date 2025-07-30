from .lib import Base


class DmIm(Base):
    def im_create_username(self, username: str):
        return self._make_request('im.create', payload={'username': username})

    def im_members(self, room_id: str):
        return self._make_request(
            'im.members',
            params={
                'roomId': room_id,
                'count': self.settings.count,
                'offset': self.settings.offset,
            },
            method='get',
        )

    def dm_create_user_id(self, user_id: str):
        return self._make_request('dm.create', payload={'userId': user_id})

    def dm_delete(self, room_id: str, type: str):
        return self._make_request('dm.delete', payload={
            'roomId': room_id,
            'type': type,  # NOTE: "soft" | "hard"
        })
