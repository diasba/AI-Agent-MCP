# test_functional_tool.py
import pytest
from tool import fetch_products_impl, Params

@pytest.mark.parametrize("filter_input, expected_filter", [
    ("type:Triangle", "triangle"),
    ("Triangle", "triangle"),
    ("  Hexagon ", "hexagon"),
    ("Available", "available"),
    ("filter:Square", "square"),
    (None, None),
    ("UnknownShape", None),  # invalid -> ignored
])
def test_filters_and_prints(filter_input, expected_filter, capsys):
    params = Params(page=1, filter=filter_input)
    result = fetch_products_impl(params)
    captured = capsys.readouterr()

    # Prüfe DEBUG-Ausgabe
    debug_line = captured.out.splitlines()[0]
    if expected_filter:
        assert f"'filter': '{expected_filter}'" in debug_line
    else:
        assert "'filter'" not in debug_line

    # Ergebnisse validieren
    # Kein Filter -> <=10 Produkte
    if expected_filter is None:
        assert len(result) <= 10
    else:
        assert len(result) > 0
        if expected_filter == "triangle":
            assert all(p.type == "Triangle" for p in result)
        elif expected_filter == "hexagon":
            assert all(p.type == "Hexagon" for p in result)
        elif expected_filter == "square":
            assert all(p.type == "Square" for p in result)
        elif expected_filter == "available":
            assert all(p.available for p in result)

@pytest.mark.parametrize("spoken, normalized", [
    ("Dreiecke", "triangle"),
    ("Kreise", "circle"),
    ("verfügbar", "available"),
])
def test_normalize_german_synonyms(spoken, normalized, capsys):
    params = Params(page=1, filter=spoken)
    result = fetch_products_impl(params)
    captured = capsys.readouterr()

    debug_line = captured.out.splitlines()[0]
    assert f"'filter': '{normalized}'" in debug_line
    assert len(result) > 0

