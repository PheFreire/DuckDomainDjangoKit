from uuid import (
    uuid4,
)
from decimal import (
    Decimal,
)
from datetime import (
    date,
    datetime,
)

from dddk.logs.jsonify import (
    jsonify,
)


def test_primitives_pass_through():
    assert jsonify(None) is None
    assert jsonify("text") == "text"
    assert jsonify(1) == 1
    assert jsonify(1.5) == 1.5
    assert jsonify(True) is True


def test_datetime_and_date_are_isoformatted():
    dt = datetime(2026, 1, 1, 12, 30)
    assert jsonify(dt) == dt.isoformat()
    d = date(2026, 1, 1)
    assert jsonify(d) == d.isoformat()


def test_uuid_and_decimal_are_stringified():
    value = uuid4()
    assert jsonify(value) == str(value)
    assert jsonify(Decimal("10.50")) == "10.50"


def test_mapping_is_recursively_jsonified_with_string_keys():
    value = uuid4()
    result = jsonify({1: "a", "id": value})
    assert result == {"1": "a", "id": str(value)}


def test_list_tuple_and_set_become_lists():
    assert jsonify([1, 2]) == [1, 2]
    assert jsonify((1, 2)) == [1, 2]
    assert jsonify({1}) == [1]


def test_nested_structures_are_fully_converted():
    dt = datetime(2026, 1, 1)
    result = jsonify({"items": [{"created_at": dt}]})
    assert result == {"items": [{"created_at": dt.isoformat()}]}


def test_unknown_object_falls_back_to_str():
    class Custom:
        def __str__(self):
            return "custom-repr"

    assert jsonify(Custom()) == "custom-repr"
