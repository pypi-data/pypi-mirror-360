import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Generator

import pytest
from git.objects.util import Actor
from git.repo import Repo

from rpo.analyzer import RepoAnalyzer


def pytest_collection_modifyitems(items: list[pytest.Function]):
    for item in items:
        if "integration" in item.listnames():
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def actors():
    actors: list[Actor] = [
        Actor(f"User{i} Lastname", f"user{i}@example.com") for i in range(3)
    ]
    return actors


@pytest.fixture(scope="session", autouse=True)
def repos_directory(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp(f"test-repos-{time.time()}-")


@pytest.fixture(scope="session")
def cpython_repo(repos_directory: Path) -> Generator[Repo]:
    remote_url = "https://github.com/python/cpython.git"
    path: str | os.PathLike[str] | None = os.getenv("LARGE_REPO_PATH")
    if not path:
        yield Repo.clone_from(remote_url, to_path=repos_directory)
    else:
        yield Repo(path)


@pytest.fixture(scope="session")
def tmp_repo(repos_directory: Path, actors: list[Actor]) -> Repo:
    d = repos_directory / "small_repo"
    d.mkdir()
    r = Repo.init(repos_directory)

    files: list[Path] = []
    for i, a in enumerate(actors):
        line_count = i + 1
        commit_date = datetime.now(UTC) + timedelta(days=(-7 + line_count))
        author_date = commit_date + timedelta(days=-1)
        f = d / f"{line_count}_line.txt"
        files.append(f)
        _ = f.write_text("\n".join(str(j) for j in range(line_count)))
        _ = r.index.add(f)
        _ = r.index.commit(
            f"test commit with {line_count} lines",
            author=actors[i],
            author_date=author_date,
            commit_date=commit_date,
            committer=actors[i],
        )

    remove_file_date = datetime.now(UTC) + timedelta(days=4)
    _ = r.index.remove(files[0])
    _ = r.index.commit(
        "remove file",
        author=actors[0],
        author_date=remove_file_date + timedelta(days=-1),
        commit_date=remove_file_date,
        committer=actors[0],
    )

    # author 3, adds one file with three lines, duplicates contents, then deletes first line
    f = files[-1]
    contents = f.read_text()
    _ = f.write_text(contents + "\n" + contents)  # duplicate text
    _ = r.index.add(f)

    actors[-1].email = "updated@example.com"
    _ = r.index.commit(
        "additions with new email", author=actors[-1], committer=actors[-1]
    )

    truncate_date = datetime.now(UTC) + timedelta(days=3)
    _ = f.write_text("\n".join(f.read_text().splitlines()[1:]))
    _ = r.index.add(f)
    _ = r.index.commit(
        "truncate_file",
        author=actors[-1],
        committer=actors[-1],
        author_date=truncate_date + timedelta(days=-1),
        commit_date=truncate_date,
    )
    return r


@pytest.fixture
def tmp_repo_analyzer(tmp_repo: Repo) -> RepoAnalyzer:
    ra = RepoAnalyzer(repo=tmp_repo, in_memory=True)
    return ra
