#!/bin/bash

git fetch --all
git reset --hard origin/master
psql -d postgres -a -f reset.sql
python3 parse.py prod