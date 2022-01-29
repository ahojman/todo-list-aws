#!/bin/bash

source todo-list-aws/bin/activate

set -x

export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ENDPOINT_OVERRIDE=""
export DYNAMODB_TABLE=todoUnitTestsTable

echo "PYTHONPATH: $PYTHONPATH"

python test/unit/TestToDo.py
pip show coverage
coverage run --include=src/todoList.py test/unit/TestToDo.py
coverage report -m
coverage xml