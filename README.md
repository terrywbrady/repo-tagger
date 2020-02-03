# repo-tagger

git log --pretty=oneline v7.0..v7.1
git rev-list -1 --before "2020-01-31" master

## tagger sprint XX [---as-of-date YYYY-MM-DD] [--since TAG]

Tag all repos with a sprint number.

- --date Retroactively tag based on a date
- --since Generate a report of changes since TAG

## tagger deploy [--deploy-date YYYY-MM-DD] [--since TAG]

Tag mrt-doc repos with deployment release.

- --since Generate a report of changes since TAG

## tagger report --since TAG [--until TAG]

Generate a report of changes since TAG

- --until TAG stop report at TAG
