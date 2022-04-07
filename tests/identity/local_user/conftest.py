import contextlib

import pytest

from cluster_agent.identity.local_user.settings import LOCAL_USER_SETTINGS


@pytest.fixture
def tweak_local_user_settings():
    """
    Provides a fixture to use as a context manager where the local user settings may be
    temporarily changed.
    """

    @contextlib.contextmanager
    def _helper(**kwargs):
        """
        Context manager for tweaking app settings temporarily.
        """
        previous_values = {}
        for (key, value) in kwargs.items():
            previous_values[key] = getattr(LOCAL_USER_SETTINGS, key)
            setattr(LOCAL_USER_SETTINGS, key, value)
        try:
            yield
        finally:
            for (key, value) in previous_values.items():
                setattr(LOCAL_USER_SETTINGS, key, value)

    return _helper
