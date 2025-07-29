import pathlib
import json
from collections import defaultdict
from typing import Callable, Dict
from github.NamedUser import NamedUser
from github.AuthenticatedUser import AuthenticatedUser
from github.Repository import Repository
from github.Commit import Commit
import requests
import os
import dbm.sqlite3 as dbm
import logging
logger = logging.getLogger(__name__)


def get_language_by_filename(filename: str) -> str:
    splitted = os.path.splitext(filename)
    if not splitted[1]:
        lang = os.path.basename(splitted[0])
    else:
        lang = splitted[1]  # Get file extension
    return lang.lower()  # Normalize to lowercase


def get_additions_of_user(user: NamedUser | AuthenticatedUser, gh_token: str, cache, get_language_by_filename: Callable[[str], str]) -> Dict[str, int]:
    cache = pathlib.Path(cache)
    usercache = cache / user.login
    os.makedirs(usercache, exist_ok=True)  # Ensure user cache directory exists
    totals = defaultdict(int)
    for repo in user.get_repos(type="public"):
        repocache = usercache / repo.full_name
        os.makedirs(repocache.parent, exist_ok=True)
        for lang, addition in get_additions_in_repo(repo, user, gh_token, repocache, get_language_by_filename).items():
            totals[lang] += addition
    return totals


def get_additions_in_repo(repo: Repository, user: NamedUser | AuthenticatedUser, gh_token: str, cache: str, get_language_by_filename: Callable[[str], str]):
    totals = defaultdict(int)
    commit_set = set()
    for branch in repo.get_branches():
        for commit in repo.get_commits(author=user.login, sha=branch.name):
            if commit.sha in commit_set:
                continue  # Skip if commit already processed
            commit_set.add(commit.sha)
            for lang, addition in get_additions_in_commit(commit, repo, gh_token, cache, get_language_by_filename).items():
                totals[lang] += addition
    return totals


def get_additions_in_commit(commit: Commit, repo: Repository, gh_token: str, cache: str, get_language_by_filename: Callable[[str], str]) -> Dict[str, int]:
    totals = defaultdict(int)
    if len(commit.parents) <= 0:
        return totals  # Skip if there are no parents (first commit)
    patch = get_patch_of_commit(commit, repo, gh_token, cache)
    for file in patch.get("files", []):
        if file["additions"] <= 0:
            continue  # Skip files with no additions
        lang = get_language_by_filename(file["filename"])
        totals[lang] += file["additions"]
    return totals


def get_patch_of_commit(commit: Commit, repo: Repository, gh_token: str, cache: str) -> Dict:
    cache_key = f"{repo.full_name}-{commit.sha}"
    with dbm.open(cache, 'c') as db:
        if cache_key in db:
            logger.info(f"Use cached {commit.sha} at {commit.commit.author.date} in {repo.name}")
            return json.loads(db[cache_key])
        else:
            patch = get_patch_of_commit_from_request(commit, repo, gh_token)
            db[cache_key] = json.dumps(patch)
            return patch


def get_patch_of_commit_from_request(commit: Commit, repo: Repository, gh_token: str) -> Dict:
    parent = commit.parents[0].sha
    url = f"https://api.github.com/repos/{repo.full_name}/compare/{parent}...{commit.sha}"
    logger.info(f"Requesting {commit.sha} at {commit.commit.author.date} in {repo.name}")
    patch = requests.get(url, headers={"Authorization": f"token {gh_token}"}).json()
    return patch
