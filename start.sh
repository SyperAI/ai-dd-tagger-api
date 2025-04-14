#!/bin/bash

PORT=5000
LOG_PATH="/var/log"
WORKERS=4

while getopts "p:l:w" opt; do
  case $opt in
    p)
      PORT=$OPTARG
      ;;
    l)
      LOG_PATH=$OPTARG
      ;;
    w)
      WORKERS=true
      ;;
    *)
      echo "-p <port> -l <path to logs dir> -w <workers amount>"
      ;;
  esac
done

source ./venv/bin/activate
gunicorn -w "$WORKERS" -b localhost:"$PORT" \
--access-logfile "$LOG_PATH"/access.log \
--error-logfile "$LOG_PATH"/error.log \
app:app