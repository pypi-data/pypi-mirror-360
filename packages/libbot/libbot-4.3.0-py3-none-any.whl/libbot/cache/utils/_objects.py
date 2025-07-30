import logging
from copy import deepcopy
from logging import Logger
from typing import Any

try:
    from ujson import dumps, loads
except ImportError:
    from json import dumps, loads

logger: Logger = logging.getLogger(__name__)

try:
    from bson import ObjectId
except ImportError:
    logger.warning(
        "Could not import bson.ObjectId. PyMongo conversions will not be supported by the cache. It's safe to ignore this message if you do not use MongoDB."
    )


def _json_to_string(json_object: Any) -> str:
    json_object_copy: Any = deepcopy(json_object)

    if isinstance(json_object_copy, dict) and "_id" in json_object_copy:
        json_object_copy["_id"] = str(json_object_copy["_id"])

    return dumps(json_object_copy, ensure_ascii=False, indent=0, escape_forward_slashes=False)


def _string_to_json(json_string: str) -> Any:
    json_object: Any = loads(json_string)

    if "_id" in json_object:
        try:
            json_object["_id"] = ObjectId(json_object["_id"])
        except NameError:
            logger.debug(
                "Tried to convert attribute '_id' with value '%s' but bson.ObjectId is not present, skipping the conversion.",
                json_object["_id"],
            )

    return json_object
