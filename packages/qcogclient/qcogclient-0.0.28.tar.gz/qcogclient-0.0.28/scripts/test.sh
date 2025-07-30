#!/bin/bash

echo "Running tests..."

verbose="$1"

if [ "$verbose" == "verbose" ]; then
    pytest -v -ss tests/
else
    pytest tests/
fi