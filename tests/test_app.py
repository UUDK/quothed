"""Tests for the first, direct Flask application milestone."""

from pathlib import Path

from quothed import create_app, load_quotes


def test_load_quotes_ignores_empty_lines(tmp_path: Path) -> None:
    """Only non-empty lines are made available as quotes."""
    quotes_file = tmp_path / "quotes.txt"
    quotes_file.write_text("First quote.\n\n  Second quote.  \n", encoding="utf-8")

    assert load_quotes(quotes_file) == ["First quote.", "Second quote."]


def test_quote_route_returns_a_quote() -> None:
    """The root route returns a styled page containing one quote."""
    client = create_app().test_client()

    response = client.get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert any(quote in page for quote in load_quotes())
    assert "style.css" in page


def test_stylesheet_is_available() -> None:
    """The page stylesheet can be served by Flask."""
    response = create_app().test_client().get("/static/style.css")

    assert response.status_code == 200
    assert "justify-content: center" in response.get_data(as_text=True)
