from pathlib import Path
from typing import List

from .lib import Base


class Groups(Base):
    def create(self, name: str, members: List[str]):
        return self._make_request('groups.create', payload={
            'name': name,
            'members': members,
        })

    def info(self, room_id: str):
        return self._make_request(
            'groups.info',
            params={
                'roomId': room_id,
                'offset': self.settings.offset,
                'count': self.settings.count,
            },
            method='get',
        )

    def members(self, room_id: str):
        return self._make_request(
            'groups.members',
            params={
                'roomId': room_id,
                'offset': self.settings.offset,
                'count': self.settings.count,
            },
            method='get',
        )

    def invite(self, room_id: str, user_id: str):
        return self._make_request('groups.invite', payload={
            'roomId': room_id,
            'userId': user_id,
        })

    def delete(self, room_id: str):
        return self._make_request('groups.delete', payload={'roomId': room_id})

    def rename(self, room_id: str, name: str):
        return self._make_request('groups.rename', payload={
            'roomId': room_id,
            'name': name,
        })

    def set_avatar(self, group_id: str, filename: Path):
        return self._upload_file_base(
            endpoint='groups.setAvatar',
            room_id=group_id,
            path=filename,
            text=None,
        )

    def convert_to_super(self, room_id: str, topic_name: str, emoji: str):
        payload = {
            'roomId': room_id,
            'defaultTopic': {
                'fname': topic_name,
                'emoji': emoji,
            },

        }
        return self._make_request(
            'groups.convertToSupergroup', payload=payload,
        )

    def add_owner(self, room_id: str, user_id: str):
        return self._make_request(
            'groups.addOwner', payload={
                'roomId': room_id,
                'userId': user_id,
            },
        )

    def kick(self, room_id: str, user_id: str):
        return self._make_request(
            'groups.kick', payload={
                'roomId': room_id,
                'userId': user_id,
            },
        )
