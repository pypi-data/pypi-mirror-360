#! /bin/bash

# Lint the code with ruff
ruff check --fix src/

# Lint the code with mypy
mypy src/
