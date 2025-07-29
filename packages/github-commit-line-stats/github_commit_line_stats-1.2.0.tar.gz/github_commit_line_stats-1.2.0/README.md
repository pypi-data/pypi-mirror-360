# GitHub Commit Line Stats

Count how many lines of code you commit on GitHub! (Count by file extension)

```sh
python -m ghcls --token <YOUR GITHUB TOKEN>
```

```sh
python -m ghcls -h
usage: __main__.py [-h] -t TOKEN [-u USER] [-c CACHE] [-o OUTPUT]

GitHub Commit Line Stats

options:
  -h, --help           show this help message and exit
  -t, --token TOKEN    GitHub Personal Access Token
  -u, --user USER      GitHub Username (Optional)
  -c, --cache CACHE    Cache directory for commits
  -o, --output OUTPUT  Output file for commit stats

```

```python
from ghcls import get_additions_of_user, get_language_by_filename
gh = Github(your_gh_token)
user = gh.get_user(your_username)
totals = get_additions_of_user(user, token, cache, get_language_by_filename)
# You can customize your language detector by changing get_language_by_filename
pathlib.Path(output).write_text(json.dumps(totals, indent=2))
```