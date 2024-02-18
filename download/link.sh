#!/bin/bash
for FILE in ../../openid-sn/python/hit-$1/*; do ln -s $FILE; done
