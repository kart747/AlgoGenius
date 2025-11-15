"""Proxy module maintained for backward compatibility.

The unit test has moved to tests/unit/test_submissions_basic.py.
Importing from this module ensures existing tooling that targets the
legacy path continues to work while the new structure is adopted.
"""

from tests.unit.test_submissions_basic import *  # noqa: F401,F403