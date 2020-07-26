#!/bin/sh

set -eu

cd "$(dirname "$0")"
exec python manage.py runserver 0.0.0.0:18000
