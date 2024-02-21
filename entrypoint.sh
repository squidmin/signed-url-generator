#!/bin/sh
# entrypoint.sh

if [ -z "${PORT}" ]; then
  echo "The PORT environment variable is not set. Defaulting to 8080."
  PORT=8080
fi

exec gunicorn --bind 0.0.0.0:$PORT app:app
