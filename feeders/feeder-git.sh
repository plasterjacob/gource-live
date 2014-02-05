#!/bin/sh -e

REMOTE=$1
BRANCH=$2
INTERVAL=$3

test "$4" && SHA=$4 || SHA=$(git rev-list $REMOTE/$BRANCH | tail -n 1)

while true
do
    for SHA in $(git rev-list --reverse --first-parent $REMOTE/$BRANCH $SHA..)
    do
        AUTHOR=$(git log --format=%an $SHA --max-count=1)
        TIMESTAMP=$(git log --format=%at $SHA --max-count=1)
        PREFIX="$TIMESTAMP|$AUTHOR|"
        git diff-tree -r --no-commit-id --name-status $SHA | tr '\t' '|' | while read SUFFIX
        do
            echo $PREFIX$SUFFIX
        done
    done
    git fetch $REMOTE >/dev/null 2>&1
    sleep $INTERVAL
done
