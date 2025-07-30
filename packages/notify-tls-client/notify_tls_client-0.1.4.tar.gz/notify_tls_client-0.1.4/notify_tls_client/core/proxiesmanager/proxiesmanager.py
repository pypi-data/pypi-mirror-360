from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Proxy:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None

    def to_proxy_dict(self):
        if self.username is None:
            return {
                'http': f'http://{self.host}:{self.port}',
                'https': f'https://{self.host}:{self.port}'
            }

        return {
            'http': f'http://{self.username}:{self.password}@{self.host}:{self.port}',
            'https': f'https://{self.username}:{self.password}@{self.host}:{self.port}'
        }


@dataclass_json
@dataclass
class ProxiesManager:
    _proxies: list[Proxy] = field(default_factory=list)
    _current_proxy_index: int = 0
    _current_proxy: Optional[Proxy] = None

    def get_next(self) -> Proxy:

        if not self._proxies:
            raise Exception('No proxies available')

        if self._current_proxy_index < len(self._proxies):
            proxy = self._proxies[self._current_proxy_index]
            self._current_proxy_index += 1
        else:
            self._current_proxy_index = 0
            proxy = self._proxies[self._current_proxy_index]

        return proxy

    def get_current_proxy(self) -> Optional[Proxy]:
        if not self._current_proxy:
            return None

        return self._current_proxy

    def set_proxies(self, proxies: list[Proxy]):
        self._proxies = proxies
        self._current_proxy_index = 0
        self._current_proxy = None

    def add_proxy(self, proxy: Proxy):
        self._proxies.append(proxy)
        self._current_proxy_index = 0
    def get_proxies(self) -> list[Proxy]:
        return self._proxies



