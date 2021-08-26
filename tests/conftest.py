import pytest

import random
import string


@pytest.fixture
def random_word():
    """
    Fixture to provide a helper method to return a
    random string containing a fixed number of chars
    """

    def _helper(length: int = 30):
        """
        Args:
            length (int): String's  final length
        """
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(length))

    return _helper
