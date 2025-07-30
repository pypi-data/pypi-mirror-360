from typing import Any

from retry_requests import retry

from labels.config.cache import dual_cache


@dual_cache
def make_get(url: str, *, content: bool = False, **kwargs: Any) -> Any | None:
    response = retry().get(url, timeout=kwargs.pop("timeout", 30), **kwargs)
    if response.status_code != 200:
        return None
    if content:
        return response.content.decode("utf-8")

    return response.json()
