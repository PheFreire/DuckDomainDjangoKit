from dddk.logs.pretty import (
    pretty,
)


def test_pretty_prints_title(capsys):
    pretty("My Title", has_line=False)
    out = capsys.readouterr().out
    assert "(My Title)" in out


def test_pretty_prints_value_when_provided(capsys):
    pretty("Title", "some value", has_line=False)
    out = capsys.readouterr().out
    assert "some value" in out


def test_pretty_omits_value_line_when_not_provided(capsys):
    pretty("Title", has_line=False)
    out = capsys.readouterr().out
    lines = [line for line in out.split("\n") if line.strip()]
    assert len(lines) == 1


def test_pretty_serializes_value_as_json_when_requested(capsys):
    pretty("Title", {"a": 1}, value_is_json=True, has_line=False)
    out = capsys.readouterr().out
    assert '"a": 1' in out
