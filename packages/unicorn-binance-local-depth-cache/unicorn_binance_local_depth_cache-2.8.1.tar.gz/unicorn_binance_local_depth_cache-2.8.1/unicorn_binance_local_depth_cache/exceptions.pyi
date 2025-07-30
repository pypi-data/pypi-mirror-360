from _typeshed import Incomplete

class DepthCacheClusterNotReachableError(Exception):
    message: str
    def __init__(self, url: Incomplete | None = None) -> None: ...

class DepthCacheOutOfSync(Exception):
    message: str
    def __init__(self, market: Incomplete | None = None) -> None: ...

class DepthCacheAlreadyStopped(Exception):
    message: str
    def __init__(self, market: Incomplete | None = None) -> None: ...

class DepthCacheNotFound(Exception):
    message: str
    def __init__(self, market: Incomplete | None = None) -> None: ...
