import time
import traceback
from datetime import datetime



def change_state_decorator(callback):
    def wrapper(*args, **kwargs):
        self = args[0]
        self.free = False
        response = callback(*args, **kwargs)
        self.free = True
        return response

    return wrapper


def print_request_infos_decorator(callback):
    def wrapper(*args, **kwargs):
        start = time.time()
        response = callback(*args, **kwargs)
        response.elapsed = round((time.time() - start) * 1000, 2)
        self = args[0]

        print("Date: ", datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")[:-3])
        print(f"Request URL: {response.url}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Elapsed Time: {response.elapsed} ms")

        if self.client.proxies:
            print(f"Proxy: {self.client.proxies['http']}")

        print(f"-")

        return response

    return wrapper


def handle_exception_requests_decorator(callback):
    def wrapper(*args, **kwargs):
        response = None
        try:
            response = callback(*args, **kwargs)
        except Exception as e:
            print(traceback.format_exc())
            self = args[0]
            self.get_tls().close()
            self._create_new_client(self.client_identifier,self.random_tls_extension_order)
            self.change_proxy()

        return response

    return wrapper


def handle_forbidden_requests_decorator(callback):
    def wrapper(*args, **kwargs):
        response = callback(*args, **kwargs)
        if response.status_code == 403 or response.status_code == 429:
            self = args[0]
            self.get_tls().close()
            self._create_new_client(self.client_identifier,self.random_tls_extension_order)

            if self.proxies_manager:
                self.change_proxy()

        return response

    return wrapper


def increment_requests_decorator(callback):
    def wrapper(*args, **kwargs):

        self = args[0]
        response = callback(*args, **kwargs)
        self.requests_amount += 1

        if self.requests_amount >= self.requests_limit_same_proxy:
            self.get_tls().close()
            self._create_new_client(self.client_identifier,self.random_tls_extension_order)
            self.change_proxy()

        return response

    return wrapper


