import os
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Sequence

import httpx
from async_lru import alru_cache
from github import Github

from ign import RAW_BASE_URL
from ign.consts import OWNER_REPO

_httpx_client_cvar = ContextVar("httpx_client")


@asynccontextmanager
async def httpx_client():
    try:
        client = _httpx_client_cvar.get()
    except LookupError:
        pass
    else:
        yield client
        return

    async with httpx.AsyncClient() as client:
        reset_token = _httpx_client_cvar.set(client)
        try:
            yield client
        finally:
            _httpx_client_cvar.reset(reset_token)


class NoCommitError(RuntimeError):
    def __init__(
        self,
        *poargs,
        owner_repo: str,
        path: str | None = None,
        sha: str | None = None,
        **kwargs,
    ):
        # noinspection PyArgumentList
        # to silence warning about **kwargs,
        # because of MRO, there may be other bases in between
        super().__init__(*poargs, **kwargs)
        self.owner_repo = owner_repo
        self.path = path
        self.sha = sha

    def __str__(self):
        msg = "No commits found"
        if self.path is not None:
            msg += f" for path {self.path}"
        msg += f" in repo {self.owner_repo}"
        if self.sha is not None:
            msg += f" at or before {self.sha}"
        super_msg = super().__str__()
        if super_msg:
            msg += f": {super_msg}"
        return msg


async def get_latest_sha(path: str | None = None, sha: str | None = None) -> str:
    github_api_token = os.getenv("GITHUB_API_TOKEN")
    with Github(login_or_token=github_api_token) as gh:
        repo = gh.get_repo(OWNER_REPO)
        params = {}
        if sha is not None:
            params["sha"] = sha
        if path is not None:
            params["path"] = path
        commits = repo.get_commits(**params)
        try:
            return commits[0].sha
        except IndexError:
            raise NoCommitError(owner_repo=OWNER_REPO, path=path, sha=sha) from None


async def get_template(
    name: str, as_of: str | None = None
) -> tuple[Sequence[str], str]:
    path = f"{name}.gitignore"
    sha = await get_latest_sha(path, as_of)
    lines = await _get_template_at_commit(path, sha)
    return lines, sha.lower()


@alru_cache
async def _get_template_at_commit(path, sha):
    async with httpx_client() as client:
        resp = await client.get(f"{RAW_BASE_URL}/{sha}/{path}")
        resp.raise_for_status()
        lines = resp.text.splitlines(keepends=True)
    return lines
