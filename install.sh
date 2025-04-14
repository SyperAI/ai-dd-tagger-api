#!/bin/bash

echo "Did you configure .service file? (Y/N/S - skip):"
read service_confirm
if [ "$service_confirm" == "N" ]; then
    echo "Configure .service file or choose to skip it to continue install."
    exit 1
elif [ "$service_confirm" == "Y" ]; then
  if [ ! -d "/etc/systemd/system" ]; then
    echo "systemd folder was not found in your system. Skipping it."
  else
    cp "./ai_dd_tagger_api.service" "/etc/systemd/system/"
  fi
fi

# Create a virtual environment
python3.11 -m venv venv

source ./venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

