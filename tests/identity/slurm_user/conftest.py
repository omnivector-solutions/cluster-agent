import contextlib

import pytest

from cluster_agent.identity.slurm_user.settings import SLURM_USER_SETTINGS


@pytest.fixture
def tweak_slurm_user_settings():
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
            previous_values[key] = getattr(SLURM_USER_SETTINGS, key)
            setattr(SLURM_USER_SETTINGS, key, value)
        try:
            yield
        finally:
            for (key, value) in previous_values.items():
                setattr(SLURM_USER_SETTINGS, key, value)

    return _helper
