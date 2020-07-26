#!/bin/sh

set -eu

cd "$(dirname "$0")"
trap 'kill 0' EXIT
python manage.py runserver 0.0.0.0:8000 &
ALLOW_PREVIEW=yes \
python manage.py runserver 0.0.0.0:8001 &
wait
