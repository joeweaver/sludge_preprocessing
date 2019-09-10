#!/usr/bin/env bash 
set -e 
if [ -z "$1" ]
then
    echo "Specify the raw image directory"
    exit
fi

if [ -d "./$1" ]
then 
    python section_average.py "./$1" ./output/sec_averages
    python plate_bg.py ./output/sec_averages ./output/plate_backgrounds
    python plate_devignette.py ./output/sec_averages ./output/plate_backgrounds/background output/final
else
    echo "Couldn't find directory: $1"
fi
