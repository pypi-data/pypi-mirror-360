from typing import Any, Union

import requests

from .lib import Base


class Different(Base):
    def version(self):
        return requests.get(f'{self.short_url}/info', verify=False)

    def preferences_list(self):
        return self._make_request('preferences.list', method='get')

    def preferences_set(self, preference: str, value: Union[int, str]):
        return self._make_request(
            'preferences.set', payload={preference: value},
        )

    def timesync(self):
        return requests.get(f'{self.short_url}/timesync', verify=False)

    def settings_public(self):
        return self._make_request(
            'settings.public',
            params={
                'offset': self.settings.offset,
                'count': self.settings.count,
            },
            method='get',
        )

    def setting_public_by_id(self, setting_id: str):
        return self._make_request(
            f'settings.public/{setting_id}', method='get',
        )

    def settings_set(self, setting_id: str, value: Any):
        return self._make_request(
            'settings.set', payload={'id': setting_id, 'value': value},
        )

    def subscriptions_read(self, room_id: str):
        return self._make_request(
            'subscriptions.read', payload={'rid': room_id},
        )
