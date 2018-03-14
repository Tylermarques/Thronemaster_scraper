#!/bin/bash

git add .
git commit -m "Automated commit message"

ssh tmarques:Lee_c1aa@10.50.50.132 << EOF
  git fetch --all
  git reset --hard origin/master
EOF



