#!/bin/bash

if [ "$1" == "requirements" ] || [ "$1" == "requirements.txt" ]; then
    sudo pip install -r requirements.txt
elif [ "$1" == "wakeword" ]; then
    PYTHONPATH=./ python -m voiceplay.recognition.wakeword.sender
else
    PYTHONPATH=./ python -m voiceplay.cli.main $@
fi
