import sys

import pytest


def skip_versions(
        *exact: tuple[int, int],
        lower_than: tuple[int, int] = None,
        higher_than: tuple[int, int] = None
) -> pytest.mark:
    """
    Skip test if Python version is in the specified range.

    :param exact: Skip test if Python version is exactly equal to any of the specified versions.
    :param lower_than: Skip test if Python version is lower than the specified version.
    :param higher_than: Skip test if Python version is higher than the specified version.

    :return: Pytest marker.
    """
    if sys.version_info[:2] in exact:
        return pytest.mark.skip(reason="Test skipped on this Python version.")
    if lower_than and sys.version_info[:2] < lower_than:
        return pytest.mark.skip(reason="Test skipped on this Python version.")
    if higher_than and sys.version_info[:2] > higher_than:
        return pytest.mark.skip(reason="Test skipped on this Python version.")
    return pytest.mark.noop()
