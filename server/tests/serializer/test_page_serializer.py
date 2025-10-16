import pytest
from serializer.page_serializer import serialize_pages


def test_single_page_basic():
    pages = {
        "Biography": {
            "TITLE": "Life of John Doe",
            "TYPE": "biography",
            "CONTENT": "Born in 1800.",
        }
    }

    result = serialize_pages(pages)
    lines = result.strip().splitlines()

    assert lines[0] == '# extended page "Biography" used by:'
    assert lines[1] == "page-ext Biography"
    assert "TITLE=Life of John Doe" in lines
    assert "TYPE=biography" in lines
    assert "CONTENT=Born in 1800." in lines
    assert lines[-1] == "end page-ext"


def test_multiple_pages():
    pages = {
        "Bio1": {"TITLE": "Bio 1", "TYPE": "summary"},
        "Bio2": {"TITLE": "Bio 2", "TYPE": "history"},
    }

    result = serialize_pages(pages)
    blocks = [block.strip() for block in result.strip().split("\n\n") if block.strip()]
    assert len(blocks) == 2
    assert blocks[0].startswith('# extended page "Bio1" used by:')
    assert blocks[1].startswith('# extended page "Bio2" used by:')


def test_empty_pages_dict():
    result = serialize_pages({})
    assert result == ""


def test_page_with_empty_content():
    pages = {"EmptyPage": {}}
    result = serialize_pages(pages)
    assert "page-ext EmptyPage" in result
    assert "end page-ext" in result
    assert "=" not in result.split("\n")[2:-1]


def test_page_with_none_values():
    pages = {"Page1": {"TITLE": None, "TYPE": "info"}}
    result = serialize_pages(pages)
    assert "TITLE=None" in result
    assert "TYPE=info" in result


def test_page_with_special_characters():
    pages = {
        "Résumé": {"TITLE": "Résumé & Overview", "CONTENT": "Café, naïve, jalapeño"}
    }
    result = serialize_pages(pages)
    assert "page-ext Résumé" in result
    assert "TITLE=Résumé & Overview" in result
    assert "CONTENT=Café, naïve, jalapeño" in result


def test_page_with_quotes_in_name():
    pages = {'"QuotePage"': {"TITLE": "Has quotes"}}
    result = serialize_pages(pages)
    assert (
        '# extended page "\\"QuotePage\\"" used by:' in result
        or 'page-ext "QuotePage"' in result
    )


def test_trailing_newlines_consistency():
    pages = {"Page": {"TITLE": "Title"}}
    result = serialize_pages(pages)
    assert not result.endswith("\n\n")
    assert result.strip().endswith("end page-ext")


def test_pages_order_is_deterministic():
    pages = {"Zpage": {"TYPE": "z"}, "Apage": {"TYPE": "a"}}
    result1 = serialize_pages(pages)
    result2 = serialize_pages(pages)
    assert result1 == result2


def test_handles_non_string_keys_and_values():
    pages = {123: {"YEAR": 2025}}
    result = serialize_pages(pages)
    assert "page-ext 123" in result
    assert "YEAR=2025" in result
