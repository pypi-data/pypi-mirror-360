from dataclasses import dataclass

__all__ = ['ProxyLayer', 'ProxyRoute']

@dataclass
class ProxyRoute:
    url: str
    port: int
    username: str = None
    password: str = None

    @property
    def full_url(self):
        if self.username and self.password:
            return f'{self.username}:{self.password}@{self.url}:{self.port}'
        return f'{self.url}:{self.port}'

    @classmethod
    def FromUrl(cls, url: str, port: int = None, username: str = None, password: str = None):
        if port is None:
            parts = url.split(':')
            port = parts[-1]
            url = ':'.join(parts[:-1])

        if not '://' in url:
            url = 'http://' + url

        if username and password:
            url = f'{username}:{password}@{url}'

        return cls(url=url, port=port, username=username, password=password)

@dataclass
class ProxyLayer:
    http: ProxyRoute = None
    https: ProxyRoute = None
    socks5: ProxyRoute = None
    no_proxy: list[str] = None

    def __post_init__(self):
        if self.no_proxy is None:
            self.no_proxy = []

    def as_linux_env(self):
        env_vars = {}
        if self.http:
            env_vars['HTTP_PROXY'] = self.http.full_url
        if self.https:
            env_vars['HTTPS_PROXY'] = self.https.full_url
        if self.socks5:
            env_vars['SOCKS5_PROXY'] = self.socks5.full_url
        if self.no_proxy:
            env_vars['NO_PROXY'] = ','.join(self.no_proxy)
        return env_vars
    
    def as_requests_proxies(self):
        linux_env = self.as_linux_env()
        proxies = {}
        
        if 'HTTP_PROXY' in linux_env:
            proxies['http'] = linux_env['HTTP_PROXY']
        if 'HTTPS_PROXY' in linux_env:
            proxies['https'] = linux_env['HTTPS_PROXY']
        if 'SOCKS5_PROXY' in linux_env:
            proxies['socks5'] = linux_env['SOCKS5_PROXY']
        if 'NO_PROXY' in linux_env:
            proxies['no_proxy'] = linux_env['NO_PROXY']
        return proxies
    
    @classmethod
    def FromLinuxEnv(cls, env_vars: dict):
        http_proxy = env_vars.get('HTTP_PROXY', None)
        https_proxy = env_vars.get('HTTPS_PROXY', None)
        socks5_proxy = env_vars.get('SOCKS5_PROXY', None)
        no_proxy = env_vars.get('NO_PROXY', '')
        
        return cls(
            http=ProxyRoute.FromUrl(http_proxy) if http_proxy else None,
            https=ProxyRoute.FromUrl(https_proxy) if https_proxy else None,
            socks5=ProxyRoute.FromUrl(socks5_proxy) if socks5_proxy else None,
            no_proxy=no_proxy.split(',') if no_proxy else []
        )