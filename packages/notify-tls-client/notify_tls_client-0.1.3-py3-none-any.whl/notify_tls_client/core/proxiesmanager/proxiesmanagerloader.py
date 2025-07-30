import traceback
from typing import Optional

from notify_tls_client.core.proxiesmanager.proxiesmanager import Proxy, ProxiesManager


class ProxiesManagerLoader:

    def from_txt(self, path: str) -> Optional[ProxiesManager]:
        try:
            proxies = []
            with open(path, 'r') as f:
                for proxy in f.read().splitlines():
                    _proxy = proxy.split(':')
                    if len(_proxy) == 2:
                        proxies.append(Proxy(host=_proxy[0],
                                             port=int(_proxy[1])))
                    elif len(_proxy) == 4:
                        proxy = Proxy(host=_proxy[0],
                                      port=int(_proxy[1]),
                                      username=_proxy[2],
                                      password=_proxy[3])

                        proxies.append(proxy)
                    else:
                        raise (ValueError('Invalid proxy format'))

            return ProxiesManager(proxies)

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return None
