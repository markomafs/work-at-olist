#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_PATH="$DIR/../"
cd ${ROOT_PATH}
pipenv install --dev
SRC_PATH="$DIR/../src"
cd ${SRC_PATH}

export BILLING_LOG_LEVEL=DEBUG
export LOG_FILE_PATH=/tmp/debug.log

pipenv run pytest --junitxml=test-results/junit/junit.xml --cov=billing/ --cov-report html:test-results/coverage/html --cov-report xml:test-results/coverage/coverage.xml