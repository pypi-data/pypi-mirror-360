from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `straddle.resources` module.

    This is used so that we can lazily import `straddle.resources` only when
    needed *and* so that users can just import `straddle` and reference `straddle.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("straddle.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
