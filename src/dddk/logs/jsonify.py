from uuid import (
    UUID,
)
from typing import (
    Any,
)
from decimal import (
    Decimal,
)
from datetime import (
    date,
    datetime,
)
from collections.abc import (
    Mapping,
)


def jsonify(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, (UUID, Decimal)):
        return str(obj)

    if isinstance(obj, Mapping):
        return {str(k): jsonify(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [jsonify(x) for x in obj]

    return str(obj)
