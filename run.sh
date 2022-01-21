#!/bin/bash  -ex
env $(cat env | xargs) ./receiver.py
