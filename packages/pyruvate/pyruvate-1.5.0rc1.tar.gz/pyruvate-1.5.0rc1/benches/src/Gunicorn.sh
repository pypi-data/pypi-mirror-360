#!/usr/bin/env bash

set -x

/py312/bin/gunicorn -w 1 -b 0.0.0.0:9808 app:application
