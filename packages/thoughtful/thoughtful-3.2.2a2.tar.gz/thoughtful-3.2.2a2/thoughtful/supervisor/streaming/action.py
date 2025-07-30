"""
This module contains an enum to define the actions available between
StreamingCallback and Fabric
"""


from enum import Enum


class Action(str, Enum):
    """
    Action - request payload attribute defining the nature of the request to fabric
    """

    STEP_REPORT = "step_report"
    """
    Report for new steps and updates on step status.
    """

    BOT_MANIFEST = "bot_manifest"
    """
    Provides the bots manifest so empower can contextualize step reports.
    """

    ARTIFACTS_UPLOADED = "artifacts_uploaded"
    """
    Describes the location of where a bot's run artifacts are uploaded.
    """

    STATUS_CHANGE = "status_change"
    """
    Notifies the consumer that the status of a bot has changed.
    """
