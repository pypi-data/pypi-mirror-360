"""
This module contains the enum that is intended to be used to set the status of
anything, and everything in Supervisor. There may be edge cases, but these
three statuses should be enough to cover all the bases.
"""


from enum import Enum


class Status(str, Enum):
    """
    Status — The status of whatever is being tracked — step, entire flow, record
    """

    SUCCEEDED = "succeeded"
    """
    The item has completed successfully.
    """

    FAILED = "failed"
    """
    The item has failed.
    """

    WARNING = "warning"
    """
    The item requires attention.
    """

    RUNNING = "running"
    """
    The item is running.
    """
