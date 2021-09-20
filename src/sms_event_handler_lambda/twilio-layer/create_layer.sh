#!/bin/bash

echo $PWD
docker run -it -v "$PWD":/var/task "lambci/lambda:build-python3.8" /bin/sh -c "pip install -r requirements.txt -t twilio-layer/python/lib/python3.9/site-packages/; exit"

