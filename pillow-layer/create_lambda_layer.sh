#!/bin/bash
# You will need Docker in order to work
docker run -v "$PWD":/var/task "lambci/lambda:build-python3.8" /bin/sh -c "pip install -r ./requirements.txt -t python/lib/python3.8/site-packages/; exit"
# Creating ZIP layer
zip -r pillow-layer.zip ./python
echo "Pillow layer generated"
