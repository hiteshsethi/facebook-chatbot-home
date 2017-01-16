#!/usr/bin/env bash
sudo apt-get install python-dev libmysqlclient-dev python-virtualenv
virtualenv env
env/bin/pip install setuptools
env/bin/pip install -r requirements.txt
cp config.sample config.py
mkdir logs