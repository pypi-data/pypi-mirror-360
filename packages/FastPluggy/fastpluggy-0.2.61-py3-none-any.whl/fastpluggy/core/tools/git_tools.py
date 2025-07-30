import logging
from dataclasses import dataclass, asdict
from typing import Optional

from loguru import logger

from fastpluggy.core.tools.system import run_command


@dataclass
class GitInfo:
    git_installed: Optional[bool] = None
    current_branch: Optional[str] = None
    current_version: Optional[str] = None
    remote_branch: Optional[str] = None
    latest_version: Optional[str] = None

    remote_branches: Optional[list] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def have_update(self) -> bool:
        return bool(self.latest_version and self.latest_version != self.current_version)


# def is_git_installed() -> bool:
#     try:
#         Git().execute(["git", "--version"])
#         return True
#     except GitCommandNotFound:
#         return False
#     except Exception as e:
#         logger.warning(f"[GitInfo] Unexpected error checking Git: {e}")
#         return False
def is_git_installed() -> bool:
    success, stdout, stderr = run_command("git --version")
    if success:
        logging.info(f"Git is installed: {stdout.strip()}")
    else:
        logging.warning(f"Git is not installed or not in PATH: {stderr.strip()}")
    return success


def get_git_versions(path: str) -> GitInfo:
    if not is_git_installed():
        logger.info("[GitInfo] Git is not installed.")
        return GitInfo(git_installed=False)
    from git import Repo, GitCommandError

    repo = Repo(path)

    # current branch (handles detached HEAD)
    try:
        current_branch = repo.active_branch.name
    except TypeError:
        # detached HEAD; fall back to raw HEAD name
        current_branch = repo.git.rev_parse("--abbrev-ref", "HEAD")

    current_version = repo.head.commit.hexsha
    remote_branch = f"origin/{current_branch}"
    latest_version = None

    try:
        repo.remotes.origin.fetch()
        latest_version = repo.git.rev_parse(remote_branch)
        remote_branches = [ref.name for ref in repo.remotes.origin.refs]
    except GitCommandError as e:
        logger.warning(f"[GitInfo] Could not fetch latest version for {remote_branch}: {e}")

    return GitInfo(
        git_installed=True,
        current_branch=current_branch,
        current_version=current_version,
        remote_branch=remote_branch,
        latest_version=latest_version,
        remote_branches=remote_branches,
    )


def get_git_info_for_module(module: "PluginState") -> GitInfo:
    if not module.git_available:
        module.git_info = GitInfo(git_installed=False)
        return module.git_info

    try:
        module.git_info = get_git_versions(str(module.path))
    except Exception as e:
        logger.warning(f"[GitInfo] Failed to retrieve Git info for plugin '{module.path}': {e}")
        module.git_info = GitInfo(git_installed=False)
        module.warning.append(str(e))

    return module.git_info
