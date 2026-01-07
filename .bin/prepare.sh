#!/bin/bash

source ../.venv/bin/activate

read -r VERSION < ../VERSION

VERSION=$(echo "$VERSION" | xargs)

poetry version "$VERSION"

BASE=$(git merge-base HEAD origin/main)

git reset "$BASE"

git add -A

git commit -m "version = \"v$VERSION\""