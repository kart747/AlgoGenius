"""Backwards-compatible wrapper for tests/integration/test_admin_features.py."""

from tests.integration.test_admin_features import test_admin_features  # type: ignore  # noqa: F401


if __name__ == "__main__":
    test_admin_features()
