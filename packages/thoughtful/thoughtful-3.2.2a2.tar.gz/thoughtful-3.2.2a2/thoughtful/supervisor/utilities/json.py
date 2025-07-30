import json
import logging
import math
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class JSONEncoder(json.JSONEncoder):
    """
    A JSON encoder that converts NaNs to None and formats datetime objects as ISO strings.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return {"_type": "decimal", "value": str(obj)}
        if isinstance(obj, Enum):
            return obj.value

        try:
            return super().default(obj)
        except Exception as e:
            logging.warning(
                "Failed to serialize object of type %s: %s",
                type(obj),
                e,
            )
            return str(obj)

    def iterencode(self, obj, _one_shot=False):
        return super().iterencode(self._nan_to_none(obj), _one_shot)

    def encode(self, obj, *args, **kwargs):
        return super().encode(self._nan_to_none(obj), *args, **kwargs)

    def _nan_to_none(self, obj):
        if isinstance(obj, dict):
            return {k: self._nan_to_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._nan_to_none(v) for v in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        return obj
