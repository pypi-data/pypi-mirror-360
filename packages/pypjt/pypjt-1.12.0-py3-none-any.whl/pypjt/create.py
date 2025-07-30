#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

import click
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv()
PACKAGE_DIR = Path(__file__).parent.absolute()
RC_DIR = PACKAGE_DIR / "resources"
__VERSION__ = "1.12.0"


class Renderer:
    def __init__(self, searchpath: str | os.PathLike[str]):
        self.searchpath = searchpath
        self.env = Environment(
            loader=FileSystemLoader(self.searchpath),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(
        self,
        template: str | os.PathLike[str],
        output_file: str | os.PathLike[str] = "",
        kwargs: dict | None = None,
    ) -> str:
        t = self.env.get_template(str(template))
        output = t.render(**(kwargs or {}))
        if output_file:
            Path(output_file).write_text(output, encoding="utf-8")
        return output


def process(**kwargs):
    project_dir = Path(kwargs["project_dir"])
    shutil.copytree(RC_DIR, project_dir)

    (project_dir / "CHANGELOG.md").touch()

    src_dir = project_dir / kwargs["project_name"]
    src_dir.mkdir()
    (src_dir / "__init__.py").touch()
    shutil.copy2(RC_DIR / ".env.template", project_dir / ".env")

    r = Renderer(searchpath=RC_DIR)
    r.render("compose.yml", project_dir / "compose.yml", kwargs)
    r.render("MANIFEST.in", project_dir / "MANIFEST.in", kwargs)
    r.render(
        "pyproject.toml",
        project_dir / "pyproject.toml",
        {**kwargs, "pypjt_version": __VERSION__},
    )
    r.render("README.rst", project_dir / "README.rst", kwargs)
    r.render(".releaserc", project_dir / ".releaserc", kwargs)
    r.render("docs/source/conf.py", project_dir / "docs/source/conf.py", kwargs)
    r.render("docs/source/index.rst", project_dir / "docs/source/index.rst", kwargs)


@click.command()
def main():
    project_name = click.prompt("Project name", type=str)
    click.echo(f"Project will create at '{Path.cwd() / project_name}'")
    project_dir = Path.cwd() / project_name
    if project_dir.exists():
        raise click.ClickException(
            f"Project dir '{project_dir}' already exists, "
            f"please choose another name or delete it first."
        )
    version = click.prompt("Version", type=str, default="0.0.1")
    author = click.prompt("Author", type=str, default="")
    email = click.prompt("Email", type=str, default="")
    description = click.prompt("Description", type=str, default="")

    process(
        **{
            "project_dir": project_dir,
            "project_name": project_name,
            "version": version,
            "author": author,
            "email": email,
            "description": description,
        }
    )


if __name__ == "__main__":
    main()
