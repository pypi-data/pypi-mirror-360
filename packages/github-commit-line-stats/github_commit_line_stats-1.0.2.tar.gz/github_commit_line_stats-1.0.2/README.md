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