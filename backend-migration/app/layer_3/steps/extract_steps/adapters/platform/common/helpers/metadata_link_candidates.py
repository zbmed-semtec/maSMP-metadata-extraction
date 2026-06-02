"""Pick first reachable URL from candidate lists (README / CHANGELOG)."""

from collections.abc import Callable


def first_reachable_url(urls: list[str], is_file_reachable_fn: Callable[[str], bool]) -> str | None:
    for url in urls:
        if is_file_reachable_fn(url):
            return url
    return None


__all__ = ["first_reachable_url"]
