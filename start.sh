#!/usr/bin/env bash
set -e
nginx
exec uv run gunicorn --bind 0.0.0.0:8080 main:app
