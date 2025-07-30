import datetime
import uuid
from typing import List, Literal, Optional

from requests import Request

from .lib import Base


class Chat(Base):
    def send_message(
            self,
            text: str,
            room_id: str,
            file_list: Optional[list[str]] = None,
    ) -> tuple[Request, str]:
        _uuid = str(uuid.uuid4())
        return self._make_request(
            'chat.sendMessage', payload={
                'message': {
                    'rid': room_id,
                    'msg': text,
                    '_id': _uuid,
                    'fileIds': file_list,
                },
            },
        ), _uuid

    def message_reply(
            self,
            text: str,
            room_id: str,
            message_id: str,
    ) -> Request:
        return self._make_request(
            'chat.sendMessage', payload={
                'message': {
                    'rid': room_id,
                    'msg': text,
                    'toReplyId': message_id,
                },
            },
        )

    def forward_message(
            self,
            room_id: str,
            to_room_id: str,
            message_ids: List[str],
            updated_ids: List[str],
    ) -> Request:
        return self._make_request(
            'chat.forwardMessages', payload={
                'roomId': room_id,
                'toForwardRoomId': to_room_id,
                'toForwardIds': message_ids,
                'forwardedIds': updated_ids,
            },
        )

    def deferred_message(
            self,
            room_id: str,
            deferr_time: datetime,
            text: Optional[str] = None,
            alias: Optional[str] = None,
            emoji: Optional[str] = None,
            avatar: Optional[str] = None,
            attachments: Optional[str] = None,
    ) -> Request:
        return self._make_request(
            endpoint='chat.deferredMessage',
            payload={
                'rid': room_id,
                'text': text,
                'alias': alias,
                'emoji': emoji,
                'avatar': avatar,
                'attachments': attachments,
                'runAt': deferr_time,
            },
        )

    def get_deferred_message(self, room_id: Optional[str] = None) -> Request:
        return self._make_request(
            endpoint='chat.deferredMessage',
            params={'rid': room_id},
            method='get',
        )

    def update_deferred_message(
            self,
            room_id: str,
            job_id: str,
            deferr_time: Optional[datetime] = None,
            text: Optional[str] = None,
            alias: Optional[str] = None,
            emoji: Optional[str] = None,
            avatar: Optional[str] = None,
            attachments: Optional[str] = None,
    ) -> Request:
        return self._make_request(
            endpoint='chat.deferredMessage',
            payload={
                'rid': room_id,
                'text': text,
                'alias': alias,
                'emoji': emoji,
                'avatar': avatar,
                'attachments': attachments,
                'runAt': deferr_time,
                'jobId': job_id,
            },
            method='put',
        )

    def delete_deferred_message(self, job_id: str) -> Request:
        return self._make_request(
            endpoint='chat.deferredMessage',
            payload={'jobId': job_id},
            method='delete',
        )

    def load_message_history(self, room_id: str) -> Request:
        return self._make_request(
            'chat.loadMessageHistory', payload={'roomId': room_id},
        )

    def pin(self, message_id: str) -> Request:
        return self._make_request(
            'chat.pinMessage', payload={'messageId': message_id},
        )

    def unpin(self, message_id: str) -> Request:
        return self._make_request(
            'chat.unPinMessage', payload={'messageId': message_id},
        )

    def get_by_id(self, message_id: str) -> Request:
        return self._make_request(
            'chat.getMessage', params={'msgId': message_id}, method='get',
        )

    def get_pinned(self, room_id: str) -> Request:
        return self._make_request(
            'chat.getPinnedMessages',
            params={
                'roomId': room_id,
                'offset': self.settings.offset,
                'count': self.settings.count,
            },
            method='get',
        )

    def react(
            self,
            emoji: str,
            message_id: str,
            room_id: str,
            should_react: bool,
    ) -> Request:
        return self._make_request(
            'chat.react', payload={
                'emoji': emoji,
                'messageId': message_id,
                'roomId': room_id,
                'shouldReact': should_react,
            },
        )

    def get_reactions(
            self,
            message_id: str,
            room_id: str,
    ) -> Request:
        return self._make_request(
            'chat.messageReactions',
            params={
                'msgId': message_id,
                'roomId': room_id,
                'offset': self.settings.offset,
                'count': self.settings.count,
            },
            method='get',
        )

    def search(self, text: str, room_id: str) -> Request:
        return self._make_request(
            'chat.search',
            params={
                'searchText': text,
                'roomId': room_id,
            },
            method='get',
        )

    def read_users(
            self,
            message_id: str,
            room_id: Optional[str] = None,
    ) -> Request:
        return self._make_request(
            'chat.messageReadUsers',
            params={
                'msgId': message_id,
                'roomId': room_id,
                'count': self.settings.count,
                'offset': self.settings.offset,
            },
            method='get',
        )

    def draft_post(
            self,
            room_id: str,
            text: str,
            draft_type: Optional[
                Literal
                [
                    'reply', 'none', 'forward', 'edit',
                ]
            ] = 'none',
            data: Optional[dict] = None,
    ) -> Request:
        return self._make_request('chat.draft', payload={
            'roomId': room_id,
            'msg': text,
            'mode': {
                'type': draft_type,
                'data': data,
            },
        })

    def draft_get(self, room_id: str) -> Request:
        return self._make_request(
            'chat.draft', params={'roomId': room_id}, method='get',
        )

    def delete_message(
            self,
            message_id: str,
            room_id: str,
            as_user: Optional[bool] = None,
    ) -> Request:
        return self._make_request(
            endpoint='chat.delete',
            payload={
                'msgId': message_id,
                'roomId': room_id,
                'asUser': as_user,
            },
        )

    def get_deleted_messages(
            self,
            room_id: str,
            since: int,
            count: int,
            offset: int,
    ) -> Request:
        return self._make_request(
            endpoint='chat.getDeletedMessages',
            params={
                'roomId': room_id,
                'since': since,
                'count': count,
                'offset': offset,
            },
            method='GET',
        )

    def chat_attachments(
            self,
            room_id: str,
            content_types: Optional[list[str]] = None,
            after_date: Optional[int] = None,
            before_date: Optional[int] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Request:
        return self._make_request(
            endpoint='chat.attachments',
            params={
                'offset': offset,
                'count': count,
            },
            payload={
                'roomId': room_id,
                'contentTypes': content_types,
                'afterDate': after_date,
                'beforeDate': before_date,
            },
        )

    def search_in_attachments(
            self,
            room_id: str,
            content_types: Optional[list[str]] = None,
            search_text: Optional[str] = None,
            after_date: Optional[int] = None,
            before_date: Optional[int] = None,
            offset: Optional[int] = None,
            count: Optional[int] = None,
    ) -> Request:
        return self._make_request(
            endpoint='chat.searchInAttachments',
            params={
                'offset': offset,
                'count': count,
            },
            payload={
                'roomId': room_id,
                'searchContextTypes': content_types,
                'searchText': search_text,
                'afterDate': after_date,
                'beforeDate': before_date,
            },
        )
