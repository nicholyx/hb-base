"""Tests for hb_base utils."""

from hb_base.utils import greet


def test_greet():
    assert greet("World") == "Hello from hb-base, World!"
