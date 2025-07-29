import contextlib
import importlib.metadata
import threading

import typer

from tgit.add import add
from tgit.changelog import changelog
from tgit.commit import commit
from tgit.config import config
from tgit.settings_command import settings
from tgit.utils import console
from tgit.version import version

app = typer.Typer(
    name="tgit",
    help="TGIT cli",
    no_args_is_help=True,
)

# Add individual commands directly to the main app
app.command("commit", help="commit changes following the conventional commit format")(commit)
app.command("version", help="bump version of the project")(version)
app.command("changelog", help="generate changelogs")(changelog)
app.command("add", help="same as git add")(add)
app.command("config", help="edit settings")(config)
app.command("settings", help="interactive settings configuration")(settings)


def version_callback(*, value: bool) -> None:
    if value:
        version_info = importlib.metadata.version("tgit")
        console.print(f"TGIT - ver.{version_info}", highlight=False)
        raise typer.Exit


@app.callback()
def main(
    *,
    _version: bool = typer.Option(
        False,
        "--version",
        help="Show version",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    def import_openai() -> None:
        with contextlib.suppress(Exception):
            import openai  # noqa: F401, PLC0415

    threading.Thread(target=import_openai).start()


if __name__ == "__main__":
    app()
