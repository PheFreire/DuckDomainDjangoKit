from dddk.utils.match_filter import (
    match_any_filter,
    unmatch_any_filter,
)


def test_match_any_filter_true_when_one_filter_fully_matches():
    filters = [{"status": "active"}, {"status": "archived"}]
    assert match_any_filter(filters, {"status": "active", "extra": 1}) is True


def test_match_any_filter_false_when_no_filter_matches():
    filters = [{"status": "active"}, {"status": "archived"}]
    assert match_any_filter(filters, {"status": "deleted"}) is False


def test_match_any_filter_requires_all_keys_in_a_single_filter_to_match():
    filters = [{"status": "active", "kind": "premium"}]
    assert (
        match_any_filter(filters, {"status": "active", "kind": "free"})
        is False
    )
    assert (
        match_any_filter(filters, {"status": "active", "kind": "premium"})
        is True
    )


def test_match_any_filter_empty_filters_list_is_false():
    assert match_any_filter([], {"status": "active"}) is False


def test_unmatch_any_filter_true_when_no_filter_matches():
    filters = [{"status": "active"}]
    assert unmatch_any_filter(filters, {"status": "deleted"}) is True


def test_unmatch_any_filter_false_when_a_filter_matches():
    filters = [{"status": "active"}]
    assert unmatch_any_filter(filters, {"status": "active"}) is False


def test_unmatch_any_filter_empty_filters_list_is_true():
    assert unmatch_any_filter([], {"status": "active"}) is True
