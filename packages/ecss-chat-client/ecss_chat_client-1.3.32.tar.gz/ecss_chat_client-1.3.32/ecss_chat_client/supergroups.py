from pathlib import Path
from typing import Optional
from urllib.request import Request

from .lib import Base


class SuperGroups(Base):
    def create(
            self,
            name: str,
            members: list[str],
            topics: list[dict],
    ) -> Request:
        return self._make_request('supergroups.create', payload={
            'supergroups': [
                {
                    'fname': name,
                    'members': members,
                    'topics': topics,
                },
            ],
        })

    def add_topics(self, room_id: str, new_topic_name: str) -> Request:
        return self._make_request('supergroups.addTopics', payload={
            'roomId': room_id,
            'topics': [
                {
                    'fname': new_topic_name,
                },
            ],
        })

    def remove_topics(self, room_id: str, topics: list[str]) -> Request:
        return self._make_request('supergroups.removeTopics', payload={
            'roomId': room_id,
            'topicIds': topics,
        })

    def get_topics(self, room_id: str) -> Request:
        return self._make_request(
            'supergroups.topics',
            params={
                'roomId': room_id,
                'sequence': 0,
                'limit': 50,
            },
            method='get',
        )

    def edit_topic(self, topic_id: str, new_topic_name: str) -> Request:
        return self._make_request('supergroups.editTopics', payload={
            'topics': [
                {
                    '_id': topic_id,
                    'fname': new_topic_name,
                },
            ],
        })

    def invite(self, room_id: str, user_ids: list[str]) -> Request:
        return self._make_request('supergroups.invite', payload={
            'roomId': room_id,
            'userIds': user_ids,
        })

    def set_avatar(self, sgp_id: str, file_path: Path) -> Request:
        return self._upload_file_base(
            endpoint='supergroups.setAvatar',
            room_id=sgp_id,
            path=file_path,
            text=None,
        )

    def rename(self, sgp_id: str, new_name: str) -> Request:
        return self._make_request('supergroups.rename', payload={
            'roomId': sgp_id,
            'name': new_name,
        })

    def add_owner(self, sgp_id: str, user_id: str) -> Request:
        return self._make_request('supergroups.addOwner', payload={
            'roomId': sgp_id,
            'userId': user_id,
        })

    def remove_owner(self, sgp_id: str, user_id: str) -> Request:
        return self._make_request('supergroups.removeOwner', payload={
            'roomId': sgp_id,
            'userId': user_id,
        })

    def convert_to_group(self, sgp_id: str) -> Request:
        return self._make_request(
            'supergroups.convertToGroup', payload={'roomId': sgp_id},
        )

    def pin_topic(
            self,
            room_id: str,
            topic_id: str,
            pin_after: Optional[str] = None,
            pin_before: Optional[str] = None,
    ) -> Request:
        return self._make_request(
            endpoint='supergroups.pinTopic',
            payload={
                'roomId': room_id,
                'topicId': topic_id,
                'pinAfter': pin_after,
                'pinBefore': pin_before,
            },
        )

    def set_pinned_topics(self, room_id: str, pinned: list[str]) -> Request:
        return self._make_request(
            endpoint='supergroups.setPinnedTopics',
            payload={
                'roomId': room_id,
                'pinned': pinned,
            },
        )
