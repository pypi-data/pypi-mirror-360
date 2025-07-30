import time
from datetime import datetime
from typing import Optional

from notify_tls_client import tls_client
from notify_tls_client.core.client import *
from notify_tls_client.core.proxiesmanager import ProxiesManager, Proxy

from notify_tls_client.tls_client.response import Response
from notify_tls_client.tls_client.settings import ClientIdentifiers
from notify_tls_client.tls_client.structures import CaseInsensitiveDict


class NotifyTLSClient:

    def __init__(self,
                 proxies_manager: Optional[ProxiesManager] = None,
                 requests_limit_same_proxy: int = 1000,
                 client_identifier: ClientIdentifiers = "chrome_133",
                 random_tls_extension_order: bool = True):

        self.client = None
        self.free = True
        self.requests_amount = 0
        self.last_request_status = 0
        self.headers = CaseInsensitiveDict({
            "User-Agent": f"tls-client/1.0.0",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Connection": "keep-alive",
        })

        self.client_identifier = client_identifier
        self.proxies_manager = proxies_manager
        self.requests_limit_same_proxy = requests_limit_same_proxy
        self.random_tls_extension_order = random_tls_extension_order
        self.current_proxy = None
        self._create_new_client(self.client_identifier, self.random_tls_extension_order)
        self.change_proxy()

    def _create_new_client(self, client_identifier: ClientIdentifiers = 'chrome_133', random_tls_extension_order: bool = False):
        self.client = tls_client.Session(client_identifier=client_identifier,
                                         random_tls_extension_order=random_tls_extension_order)

    def set_requests_limit_same_proxy(self, requests_limit_same_proxy: int):
        self.requests_limit_same_proxy = requests_limit_same_proxy

    def set_proxies_manager(self, proxies_manager: ProxiesManager):
        self.proxies_manager = proxies_manager


    def change_proxy(self):
        if self.proxies_manager and self.proxies_manager.get_proxies():
            self.current_proxy = self.proxies_manager.get_next()
            self.client.proxies = self.current_proxy.to_proxy_dict()
            self.requests_amount = 0

    def set_proxies(self, proxies: Proxy):
        self.client.proxies = proxies.to_proxy_dict()

    def set_headers(self, headers: dict):
        self.client.headers = CaseInsensitiveDict(headers)

    def get_cookies(self):
        return self.client.cookies

    def get_cookie_by_name(self, name: str):
        return self.client.cookies.get(name)

    @handle_exception_requests_decorator
    @increment_requests_decorator
    @handle_forbidden_requests_decorator
    @print_request_infos_decorator
    @change_state_decorator
    def get(self, url: str, **kwargs) -> Response:
        start = time.time()
        response = self.client.get(url, **kwargs)
        response.elapsed = round((time.time() - start) * 1000, 2)
        self.last_request_status = response.status_code
        return response

    @handle_exception_requests_decorator
    @increment_requests_decorator
    @handle_forbidden_requests_decorator
    @print_request_infos_decorator
    @change_state_decorator
    def post(self, url: str, **kwargs) -> Response:
        start = time.time()
        response = self.client.post(url, **kwargs)
        response.elapsed = round((time.time() - start) * 1000, 2)

        self.last_request_status = response.status_code
        return response

    @handle_exception_requests_decorator
    @increment_requests_decorator
    @handle_forbidden_requests_decorator
    @print_request_infos_decorator
    @change_state_decorator
    def put(self, url: str, **kwargs) -> Response:
        start = datetime.now()
        response = self.client.put(url, **kwargs)
        response.elapsed = datetime.now() - start

        self.last_request_status = response.status_code
        return response

    @increment_requests_decorator
    @handle_forbidden_requests_decorator
    @print_request_infos_decorator
    @change_state_decorator
    def delete(self, url: str, **kwargs) -> Response:
        start = time.time()
        response = self.client.delete(url, **kwargs)
        response.elapsed = round((time.time() - start) * 1000, 2)

        self.last_request_status = response.status_code
        return response

    @handle_exception_requests_decorator
    @increment_requests_decorator
    @handle_forbidden_requests_decorator
    @print_request_infos_decorator
    @change_state_decorator
    def patch(self, url: str, **kwargs) -> Response:
        start = datetime.now()
        response = self.client.patch(url, **kwargs)
        response.elapsed = datetime.now() - start

        self.last_request_status = response.status_code
        return response

    def _change_to_free(self):
        self.free = True

    def _change_to_busy(self):
        self.free = False

    def get_cookie_value_by_name(self, name: str):
        return self.client.cookies.get(name)

    def set_cookie(self, name: str, value: str):
        self.client.cookies.set(name, value)

    def get_tls(self):
        return self.client
