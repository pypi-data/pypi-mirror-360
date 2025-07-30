# RPO: Repository Participation Observer

[![Python application](https://github.com/crlane/rpo/actions/workflows/uv-python-app.yml/badge.svg)](https://github.com/crlane/rpo/actions/workflows/uv-python-app.yml)
A command line tool and Python library to help you analyze and visualized Git repositories. Ever wondered who has most contributions? How participation has changed over time? What are the hotspots in your code that change frequently? Who has the highest bus factor? `rpo` can help.

> NOTE: This is alpha software under active development. There will be breaking changes.

## Usage

### CLI

```bash
Usage: rpo [OPTIONS] COMMAND [ARGS]...

Options:
  -r, --repository PATH
  -b, --branch TEXT
  --allow-dirty              Proceed with analyis even if repository has
                             uncommitted changes
  File selection:            Give you control over which files should be
                             included in your analysis
    -g, --glob TEXT          File path glob patterns to INCLUDE. If specified,
                             matching paths will be the only files included in
                             aggregation.            If neither --glob nor
                             --xglob are specified, all files will be included
                             in aggregation. Paths are relative to root of
                             repository.
    -xg, --xglob TEXT        File path glob patterns to EXCLUDE. If specified,
                             matching paths will be filtered before
                             aggregation.            If neither --glob nor
                             --xglob are specified, all files will be included
                             in aggregation. Paths are relative to root of
                             repository.
    --exclude-generated      If set, exclude common generated files like
                             package-manager generated lock files from
                             analysis
  Data selection:            Control over how repository data is aggregated
                             and sorted
    -A, --aggregate-by TEXT  Controls the field used to aggregate data
    -I, --identify-by TEXT   Controls the field used to identify auhors.
    -S, --sort-by TEXT       Controls the field used to sort output
  Plot options:              Control plot output, if available
    -p, --plot PATH          The directory where plot output visualization
                             will live. Either a filename ending with '.png'
                             or a directory.
  Output options:            Control how data is displayed or saved
    --save-as FILE           Save the report data to the path provided; format
                             is determined by the filename extension,
                             which must be one of (.json|.csv). If no save-as
                             path is provided, the report will be printed to
                             stdout
  -c, --config FILE          The location of the json formatted config file to
                             use. Defaults to a hidden config.json file in the
                             current working directory. If it exists, then
                             options in the config file take precedence over
                             command line flags.
  --help                     Show this message and exit.

Commands:
  activity-report   Produces file or author report of activity at a...
  cumulative-blame  Computes the cumulative blame of the repository over...
  punchcard         Computes commits for a given user by datetime
  repo-blame        Computes the per user blame for all files at a given...
  revisions         List all revisions in the repository
  summary           Generate very high level summary for the repository
  ```

### Library

```bash
pip install rpo
```

```python
from rpo import RepositoryAnalyzer

ra = RepoAnalyser("./path/to_git_repo")


```
## Examples

> NOTE: depending on your shell, you may or may not need to escape the splat character in the glob patterns used below.

See [test_cli.sh](./test_cli.sh) for more examples.

### Git Blame for all Files in a Repo at a Given Revision, Identify Users by Email
```
$ rpo -r ../my-local-repo -R HEAD -I email repo-blame
```

### Cumulative Git Blame for all Files in a Repo at a Given Revision, Identify Users by Name
```
$ rpo -r ../my-local-repo cumulative-blame
```

### Author Activity Report, Including Only Files that Match a Pattern
```
$ rpo -r ../my-local-repo -g tests/\* activity-report
```

### Author Activity Report, Excluding Files that Match a Pattern
```
$ rpo -r ../my-local-repo -xg tests/\* activity-report
```

### File Activity Report, Excluding Files that Match a Pattern
```
$ rpo -r ../my-local-repo -xg tests/\* activity-report -t files
```


## Features
- [ ] Automatically generate aliases that refer to the same person
- [x] Support analyzing by glob
- [x] Support excluding by glob
- [x] Produce blame charts
- [x] Optionally ignore merge commits
- [x] Optionally ignore whitespace
- [ ] Identify major refactorings
- [ ] Fast execution, even on giant repositories


## Performance

The goal is for the library to work even on the largest libraries. In general, the performance is proportional to the number of authors, commits, and files being considered in the aggregations.

The authors regularly [test](./tests/integration/test_cpython_repository.py) using the [cpython repository](https://github.com/python/cpython), which contains over 1,000,000 objects. That takes a while.

> TODO: Performance graphs

## Similar Projects and Inspiration

- [GitPandas](https://github.com/wdm0006/git-pandas)
- [git-truck](https://github.com/git-truck)
- [busfactor](https://github.com/SOM-Research/busfactor)
- [bus-factor-explorer](https://github.com/JetBrains-Research/bus-factor-explorer)

## References

### Git Commands

These are useful for validating results reported here. The git man pages for various commands is helpful reading.

All the files edited in a revision
```bash
git diff-tree --no-commit-id --name-only HEAD~1 -r
```

All the files _present_ at a particular revision
```bash
git ls-tree -rlt HEAD
```

All commits reachable from a revision
```bash
git rev-list HEAD --count
```

Count all commits reachable from a revision
```bash
git rev-list HEAD --count
```

All commits that touch a particular object (tree in this case)
```bash
git rev-list HEAD img
```

All files at each commit
```bash
git rev-list HEAD | xargs -r -I % git ls-tree -rt --name-only %
```

```bash
git cat-file --batch-all-objects --batch-check --unordered
```

```bash
git rev-list --all --objects --filter=object:type=blob HEAD | git cat-file --batch-check="%(objectname) %(objecttype) %(rest) %(deltabase)"
```
