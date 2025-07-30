#!/usr/bin/env bash

# detect the root of the repository
REPO_ROOT=$(git rev-parse --show-toplevel)

# creatate a virtual environment in the repository root
python3 -m venv "$REPO_ROOT/.test-venv"

source "$REPO_ROOT/.test-venv/bin/activate"

# install the package we built in the repository root
pip3 install -e "$REPO_ROOT"
pip3 install -r "$REPO_ROOT/requirements.txt"
