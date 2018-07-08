#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SRC_PATH="$DIR/../src"
cd ${SRC_PATH}
pytest --junitxml=test-results/junit/junit.xml --cov=billing/ --cov-report html:test-results/coverage/html --cov-report xml:test-results/coverage/coverage.xml