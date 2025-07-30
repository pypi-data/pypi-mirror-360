"""
This module contains the ``Record`` class, a non-user facing class that is used
to store information about a step's record. This class is represented in the
run report as a json object.

.. code-block:: json

    {
        "workflow": [
            {
                "step_id": "1.1",
                "step_status": "succeeded",
                "record": {
                    "id": "1",
                    "status": "succeeded",
                    "message": "Message can provide additional information",
                    "metadata": {
                        "internal_reason": "record amount is too low",
                        "amount": 15
                    }
                }
            }
        ]
    }

"""
import json
import logging
import warnings
from dataclasses import dataclass, field
from typing import Dict, Optional

from thoughtful.supervisor.reporting.status import Status
from thoughtful.supervisor.utilities.json import JSONEncoder


@dataclass
class Record:
    """
    A record can refer to any object that is being processed by a step. If a
    step in your workflow is repeating many times for different items, then
    each item you're iterating over can be a record.
    """

    record_id: str
    """
    str: The status of the record.
    """

    status: Status
    """
    Status: The status of the record.
    """

    message: Optional[str] = field(default_factory=str)
    """
    Message: A message that can provide additional information about the record,
    such as a (short) description of why the record is in a certain state.
    """

    # make required default = {} ?
    metadata: Optional[dict] = field(default_factory=dict)
    """
    Metadata: A dictionary of additional information about the record. This is
    mostly meant to "tag" the record for later analysis and grouping.
    """

    def __post_init__(self):
        """
        Validate the record message length
        """
        if len(self.message) > 120:
            warnings.simplefilter("always", UserWarning)
            warnings.warn(
                "Record Message Field - Please note that exceeding the character limit of 120 may result in the message being truncated in the UI"
            )
            warnings.resetwarnings()
        validate_metadata_json_helper(self.metadata)

    def __json__(self):
        return {
            "id": self.record_id,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata,
        }


def validate_metadata_json_helper(item: Dict):
    """
    Validates that the metadata field is a valid JSON object and that it is less
    than 5 KB
    """
    try:
        json_str = json.dumps(item, cls=JSONEncoder)
        if len(json_str) / 1024 > 5:
            warnings.simplefilter("always", UserWarning)
            warnings.warn(
                "Record metadata validation failed - Object should not exceed 5 KB",
                category=UserWarning,
            )
            warnings.resetwarnings()
    except Exception as e:
        logging.exception(e)
        warnings.simplefilter("always", UserWarning)
        warnings.warn(
            "Could not serialize record metadata into JSON", category=UserWarning
        )
        warnings.resetwarnings()
