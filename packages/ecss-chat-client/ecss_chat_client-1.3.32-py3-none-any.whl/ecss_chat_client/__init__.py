"""ECSS Chat Client - Python клиент для ECSS Chat."""

from .auth import Auth
from .avatar import Avatar
from .chat import Chat
from .config import Settings
from .different import Different
from .dm_im import DmIm
from .folders import Folders
from .groups import Groups
from .info import ApiInfo
from .polls import Polls
from .rooms import Rooms
from .spotlight import Spotlight
from .supergroups import SuperGroups
from .testing import Testing
from .threads import Threads
from .tus import TusService
from .users import Users
from .websocket_client import WebsocketClient


class Client:
    def __init__(
            self,
            server,
            username,
            password,
            port='3443',
            proto='https',
            verify=True,
    ):
        self.username = username
        self.password = password
        self.port = port
        self.proto = proto
        self.verify = verify
        self.server = server
        self.base_url = f'{proto}://{server}:{port}/api/v1'
        self.short_url = f'{proto}://{server}:{port}/api'
        self.__websocket_url = f'wss://{server}:{port}/websocket'

        self.settings = Settings(
            server, config_file='settings.ini',
        )

        self.session = Auth.session(
            username,
            password,
            server,
            proto,
            port,
            verify,
        )
        self.websocket = WebsocketClient(
            self.__websocket_url,
            username=self.username,
            session=self.session,
        )
        self.avatar = Avatar(self)
        self.dm_im = DmIm(self)
        self.groups = Groups(self)
        self.polls = Polls(self)
        self.rooms = Rooms(self)
        self.supergroups = SuperGroups(self)
        self.folders = Folders(self)
        self.users = Users(self)
        self.different = Different(self)
        self.chat = Chat(self)
        self.threds = Threads(self)
        self.testing = Testing(self)
        self.spotlight = Spotlight(self)
        self.tus = TusService(self)
        self.api_info = ApiInfo(self)


__all__ = ['Client']
__version__ = '1.0.0'
__author__ = 'Eltex SC VoIP'
__description__ = 'ElphChat API Client Library'
