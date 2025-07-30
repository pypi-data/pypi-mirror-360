from enum import StrEnum


class FolderTypes(StrEnum):
    """Типы папкок в чате."""

    GROUPS = 'g'
    DIRECTS = 'd'
    HIDDEN = 'h'
    ALL = 'a'
    CUSTOM = 'c'
    UNREAD = 'u'  # /pages/viewpage.action?pageId=130365575


class RoomTypes(StrEnum):
    """Типы комнат в чате."""

    DIRECT = 'd'
    PRIVATE = 'p'
    TELECONFERENCE = 'tc'
    SUPERGROUP = 's'
    TOPIC = 't'
    THREAD_ROOM = 'thread'


class SpotlightSchemas(StrEnum):
    """Типы доступных целей поиска в Spotlight."""

    ALL_USERS = 'users'
    UNKNOWN_USERS = 'unknown-users'
    DIRECT = 'rooms-d'
    PRIVATE = 'rooms-p'
    TELECONFERENCE = 'rooms-tc'
    SUPERGROUP = 'rooms-s'
    TOPIC = 'rooms-t'
    THREAD_ROOM = 'rooms-thread'
    GROUPS = 'groups'
    MESSAGES = 'messages'
