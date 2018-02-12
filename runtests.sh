#!/usr/bin/env bash

set -e

# check code style
flake8

# run tests
tox

# get full coverage stats
coverage combine
coverage report
