#!/bin/bash

if [ "$1" == "requirements" ] || [ "$1" == "requirements.txt" ]; then
    sudo pip install -r requirements.txt
else
    PYTHONPATH=./ python -m voiceplay.cli.main $@
fi
