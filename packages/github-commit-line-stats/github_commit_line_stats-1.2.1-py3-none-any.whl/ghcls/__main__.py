import pathlib
import json
import importlib
from github import Github  # pip install PyGitHub
from github.GithubObject import NotSet
from .ghcls import get_additions_of_user


def main(token: str, user: str = None, cache: str = "commitcache", output: str = "ghcls.json", language: str = "importlib.import_module('ghcls').get_language_by_filename"):
    gh = Github(token)
    user = gh.get_user(user or NotSet)
    get_language_by_filename = eval(language)
    totals = get_additions_of_user(user, token, cache, get_language_by_filename)
    pathlib.Path(output).write_text(json.dumps(totals, indent=2))


if __name__ == "__main__":
    import logging
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="GitHub Commit Line Stats")
    parser.add_argument("-t", "--token", type=str, required=True, help="GitHub Personal Access Token")
    parser.add_argument("-u", "--user", type=str, default=None, help="GitHub Username (Optional)")
    parser.add_argument("-c", "--cache", type=str, default="commitcache", help="Cache directory for commits")
    parser.add_argument("-o", "--output", type=str, default="ghcls.json", help="Output file for commit stats")
    parser.add_argument(
        "-l", "--language", type=str, default="importlib.import_module('ghcls').get_language_by_filename",
        help="Language detection function (default: importlib.import_module('ghcls').get_language_by_filename)")
    args = parser.parse_args()
    main(args.token, args.user, args.cache, args.output, args.language)
