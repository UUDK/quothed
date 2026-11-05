"""The Quothed Flask application."""

from pathlib import Path
import random

from flask import Flask, render_template


QUOTES_FILE = Path(__file__).with_name("quotes.txt")


def load_quotes(quotes_file: Path = QUOTES_FILE) -> list[str]:
    """Load non-empty quotes, using one quote per line."""
    return [
        line.strip()
        for line in quotes_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    @app.get("/")
    def quote() -> str:
        """Render one randomly selected quote in the application page."""
        return render_template("index.html", quote=random.choice(load_quotes()))

    return app


app = create_app()


def main() -> None:
    """Run the development server when invoked as a Python entry point."""
    app.run()
