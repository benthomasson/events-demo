#!/bin/bash  -ex
env $(cat env | xargs) ./sendit.sh
env $(cat env | xargs) ./receiver.py
