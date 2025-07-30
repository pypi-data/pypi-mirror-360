from contextlib import contextmanager
from os import chdir
from pathlib import Path

import pytest
import toml

from scripts.update_version import (
    format_cargo_version,
    format_python_version,
    update_version_python,
    update_version_rust,
)


@contextmanager
def change_pwd(new_pwd: Path):
    old_pwd = Path.cwd()
    try:
        chdir(new_pwd)
        yield
    finally:
        chdir(old_pwd)


@pytest.mark.parametrize(
    "input_version,expected",
    [
        ("1.2.3", "1.2.3"),
        ("1.2", "1.2.0"),
        ("1.2.3-alpha.1", "1.2.3-a1"),
        ("1.2.3-beta.2", "1.2.3-b2"),
        ("1.2.3.post1", "1.2.3-post1"),
        ("1.2.3.dev4", "1.2.3-dev4"),
        ("1.2.3-alpha.1.post2.dev3", "1.2.3-a1-post2-dev3"),
    ],
)
def test_format_cargo_version(input_version, expected):
    assert format_cargo_version(input_version) == expected


def test_update_version_rust(tmp_path: Path):
    cargo_text = """
        [package]
        name = "mountaineer"
        # Bumped automatically by CI on a release
        version = "0.1.0"
        edition = "2021"

        [dependencies]
        v8 = "0.89.0"
        deno_core_icudata = "0.73.0"
        """

    cargo_path = tmp_path / "Cargo.toml"
    cargo_path.write_text(cargo_text)

    with change_pwd(tmp_path):
        update_version_rust("0.2.0")

    assert toml.loads(cargo_path.read_text()) == {
        "package": {
            "name": "mountaineer",
            "version": "0.2.0",
            "edition": "2021",
        },
        "dependencies": {
            "v8": "0.89.0",
            "deno_core_icudata": "0.73.0",
        },
    }


@pytest.mark.parametrize(
    "input_version,expected",
    [
        ("1.2.3", "1.2.3"),
        ("1.2.3a1", "1.2.3b1"),
        ("1.2.3b2", "1.2.3b2"),
        ("1.2.3rc3", "1.2.3b3"),
        ("1.2.3.post1", "1.2.3.post1"),
        ("1.2.3.dev4", "1.2.3.dev4"),
        ("1.2.3a1.post2.dev3", "1.2.3b1.post2.dev3"),
    ],
)
def test_format_python_version(input_version, expected):
    assert format_python_version(input_version) == expected


def test_update_version_python(tmp_path: Path):
    pyproject_text = """
        [tool.poetry]
        name = "mountaineer"
        version = "0.1.0"
        description = ""
        readme = "README.md"

        [tool.poetry.dependencies]
        uvicorn = { extras = ["standard"], version = "^0.27.0.post1" }
        fastapi = "^0.68.0"
        """

    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_text)

    with change_pwd(tmp_path):
        update_version_python("0.2.0")

    assert toml.loads(pyproject_path.read_text()) == {
        "tool": {
            "poetry": {
                "name": "mountaineer",
                "version": "0.2.0",
                "description": "",
                "readme": "README.md",
                "dependencies": {
                    "uvicorn": {
                        "extras": ["standard"],
                        "version": "^0.27.0.post1",
                    },
                    "fastapi": "^0.68.0",
                },
            },
        },
    }


def test_update_version_python_with_project_version(tmp_path: Path):
    pyproject_text = """
        [tool.poetry]
        name = "mountaineer"
        version = "0.1.0"
        description = ""
        readme = "README.md"

        [project]
        name = "mountaineer"
        version = "0.1.0"
        description = ""

        [tool.poetry.dependencies]
        uvicorn = { extras = ["standard"], version = "^0.27.0.post1" }
        fastapi = "^0.68.0"
        """

    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_text)

    with change_pwd(tmp_path):
        update_version_python("0.2.0")

    assert toml.loads(pyproject_path.read_text()) == {
        "tool": {
            "poetry": {
                "name": "mountaineer",
                "version": "0.2.0",
                "description": "",
                "readme": "README.md",
                "dependencies": {
                    "uvicorn": {
                        "extras": ["standard"],
                        "version": "^0.27.0.post1",
                    },
                    "fastapi": "^0.68.0",
                },
            },
        },
        "project": {
            "name": "mountaineer",
            "version": "0.2.0",
            "description": "",
        },
    }


def test_update_version_python_only_project(tmp_path: Path):
    pyproject_text = """
        [project]
        name = "mountaineer"
        version = "0.1.0"
        description = ""
        """

    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_text)

    with change_pwd(tmp_path):
        update_version_python("0.2.0")

    assert toml.loads(pyproject_path.read_text()) == {
        "project": {
            "name": "mountaineer",
            "version": "0.2.0",
            "description": "",
        },
    }


def test_update_version_python_only_poetry(tmp_path: Path):
    pyproject_text = """
        [tool.poetry]
        name = "mountaineer"
        version = "0.1.0"
        description = ""
        """

    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_text)

    with change_pwd(tmp_path):
        update_version_python("0.2.0")

    assert toml.loads(pyproject_path.read_text()) == {
        "tool": {
            "poetry": {
                "name": "mountaineer",
                "version": "0.2.0",
                "description": "",
            },
        },
    }


def test_update_version_python_no_version_sections(tmp_path: Path, capsys):
    pyproject_text = """
        [build-system]
        requires = ["poetry-core"]
        build-backend = "poetry.core.masonry.build"
        """

    pyproject_path = tmp_path / "pyproject.toml"
    pyproject_path.write_text(pyproject_text)

    with change_pwd(tmp_path):
        update_version_python("0.2.0")

    # Verify the warning was printed
    captured = capsys.readouterr()
    assert "Neither [tool.poetry] nor [project] sections found" in captured.out

    # Verify the file wasn't modified
    assert toml.loads(pyproject_path.read_text()) == {
        "build-system": {
            "requires": ["poetry-core"],
            "build-backend": "poetry.core.masonry.build",
        },
    }
