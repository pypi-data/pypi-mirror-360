import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_creates_toc(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Title\n")
    toc_path = tmp_path / "toc.json"

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "update_docs.cli", "--docs", str(docs), "--toc", str(toc_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert toc_path.exists()
    data = json.loads(toc_path.read_text())
    assert data[0]["file"] == "index.md"


def test_cli_creates_markdown_toc(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Title\n")
    toc_json = tmp_path / "toc.json"
    toc_md = tmp_path / "toc.md"

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "update_docs.cli",
            "--docs",
            str(docs),
            "--toc",
            str(toc_json),
            "--toc-md",
            str(toc_md),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert toc_md.exists()
    content = toc_md.read_text()
    assert "[index.md](docs/index.md)" in content
    md_content = (docs / "index.md").read_text().splitlines()[0]
    assert "[Back to TOC]" in md_content


def test_cli_from_nested_dir(tmp_path):
    root = tmp_path
    (root / ".git").mkdir()
    docs = root / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Title\n")
    toc_path = root / "toc.json"

    nested = docs / "nested"
    nested.mkdir()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)

    result = subprocess.run(
        [sys.executable, "-m", "update_docs.cli", "--docs", "docs", "--toc", "toc.json"],
        cwd=nested,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert toc_path.exists()
    data = json.loads(toc_path.read_text())
    assert data[0]["file"] == "index.md"

