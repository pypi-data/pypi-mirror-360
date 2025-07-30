"""Tests for `pydantictypes` package."""

from __future__ import annotations

from typing import Any


def test_content(response: dict[Any, Any] | None) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup  # noqa: ERA001
    # assert 'GitHub' in BeautifulSoup(response.content).title.string  # noqa: ERA001
    del response
