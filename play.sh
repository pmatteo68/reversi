#!/bin/bash

cd "$(dirname "$0")"
. ./bin/env.sh
source ${VENV_NAME}/bin/activate

python src/main.py "$@"
