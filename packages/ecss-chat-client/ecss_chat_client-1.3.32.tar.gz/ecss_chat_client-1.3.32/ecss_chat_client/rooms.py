import json
import uuid
from pathlib import Path
from typing import List, Optional, Union

from .lib import Base
from .types import RoomTypes


class Rooms(Base):
    def members(self, room_id: str):
        return self._make_request(
            'rooms.members',
            params={
                'roomId': room_id,
                'count': self.settings.count,
                'offset': self.settings.offset,

            },
            method='get',
        )

    def room_sync_preview(
            self,
            hidden_rooms: str = 'include',
            room_types: List[RoomTypes] = [
                RoomTypes.DIRECT,
                RoomTypes.PRIVATE,
                RoomTypes.TELECONFERENCE,
            ],
            alerted_only: bool = False,
            updated_since: int = 0,
            sort_lm: int = 1,
            sortstarred: int = 1,
            folder_id: str = 'all',
            exclude: List[str] = [],
    ):
        return self._make_request('rooms.sync', payload={
            'preview': {
                'hidenRooms': hidden_rooms,
                'roomTypes': room_types,
                'alertedOnly': alerted_only,
                'updatedSince': updated_since,
                'sortlm': sort_lm,
                'sortstarred': sortstarred,
                'offset': self.settings.offset,
                'count': self.settings.count,
                'except': exclude,
                'folderId': folder_id,
            },
        })

    def room_sync_list(
            self,
            alerted_only: bool = False,
            folder_id: str = '',
            exclude: List[Optional[str]] = [],
            room_type: List[RoomTypes] = [
                RoomTypes.DIRECT,
                RoomTypes.PRIVATE,
                RoomTypes.TELECONFERENCE,
                RoomTypes.SUPERGROUP,
            ],
            required: Optional[list[str]] = None,
    ):
        return self._make_request('rooms.sync', payload={
            'list': {
                'alertedOnly': alerted_only,
                'offset': self.settings.offset,
                'count': self.settings.count,
                'except': exclude,
                'folderId': folder_id,
                'roomTypes': room_type,
            },
            'required': {
                'byIds': required,
            },
            'removed': {},
        })

    def room_sync_required(
            self,
            req: str,
            objects: List[str] = [],
    ):
        if req == 'saved':
            payload = {
                'required': {
                    'saved': True,
                },
            }
        if req == 'support':
            payload = {
                'required': {
                    'support': True,
                },
            }
        if req == 'byIds':
            payload = {
                'required': {
                    'byIds': objects,
                },
            }
        if req == 'byRoomName':
            payload = {
                'required': {
                    'byRoomName': objects,
                },
            }
        return self._make_request('rooms.sync', payload=payload)

    def room_sync_alerts(self):
        return self._make_request(
            'rooms.sync',
            payload={
                'alerts':
                {
                    'updatedSince': 0,
                },
            })

    def room_sync_alerted_rooms(self):
        return self._make_request(
            'rooms.sync',
            payload={
                'alertedRooms':
                {
                    'total': True,
                },
            })

    def room_sync_removed(self):
        return self._make_request('rooms.sync', payload={
            'removed': {
                'deletedSince': 0,
                'offset': self.settings.offset,
                'count': self.settings.count,
            },
        })

    def room_sync_info(self, room_id: str):
        return self._make_request(
            'rooms.info', params={'roomId': room_id}, method='get',
        )

    def invite_to_many(self, room_ids: list[str], user_ids: list[str]):
        return self._make_request(
            endpoint='rooms.inviteToMany',
            payload={
                'roomIds': room_ids,
                'userIds': user_ids,
            },
        )

    def leave(self, room_id: str):
        return self._make_request(
            'rooms.leave',
            payload={'roomId': room_id},
        )

    def set_notifications(self, room_id: str, mute: bool = False):
        return self._make_request(
            'rooms.setNotifications',
            payload={'roomId': room_id, 'mute': mute},
        )

    def my_rooms(self):
        return self._make_request(
            'rooms.myRoomsWithOtherUser',
            params={
                'userId': self.client.session.uid,
                'offset': self.settings.offset,
                'count': self.settings.count,
            },
            method='get',
        )

    def search_in_my_rooms(
            self,
            folder_id: Optional[str] = None,
            exclude_folder_id: Optional[str] = None,
            query: Optional[str] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ):
        return self._make_request(
            'rooms.searchInMyRooms',
            params={
                'folderId': folder_id,
                'excludeFolderId': exclude_folder_id,
                'query': query,
                'offset': offset,
                'count': count,
            },
            method='get',
        )

    def setting(self, room_id: str, arg: str = '', value: str = ''):
        return self._make_request(
            'rooms.saveRoomSettings',
            payload={
                'rid': room_id,
                arg: value,
            },
        )

    def pin(self, folder_id: str, room_id: str, position: int = 0):
        return self._make_request(
            'rooms.pin', payload={
                'folderId': folder_id,
                'roomId': room_id,
                'position': position,
            },
        )

    def unpin(self, folder_id: str, room_id: str):
        return self._make_request(
            'rooms.pin', payload={
                'folderId': folder_id,
                'roomId': room_id,
            },
        )

    def upload_file(self, room_id: str, text: str, path: Path):
        return self._upload_file_base('rooms.upload', room_id, path, text)

    def upload_speech(
            self,
            room_id: str,
            text: str,
            path: Path,
            waveform: dict,
            reply_id: Union[str, None] = None,
    ):
        extra_data = {
            '_id': str(uuid.uuid4()),
            'waveform': json.dumps(waveform),
        }
        if reply_id:
            extra_data['toReplyId'] = reply_id
        return self._upload_file_base(
            'rooms.uploadSpeech', room_id, path, text, extra_data,
        )
