"""Backwards-compatible wrapper for tests/integration/test_access_control.py."""

from tests.integration.test_access_control import test_access_control  # type: ignore  # noqa: F401


if __name__ == "__main__":
    test_access_control()
