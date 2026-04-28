#!/run/current-system/sw/bin/bash
LOCAL="${0%/*}/ADPIO_EDGE"
DEBUG=${1:-"release"} # release, debug
VERSION=${2:-"0.0"}


echo $LOCAL
echo "Mode: "$DEBUG


if [[ "$DEBUG" == "release" ]]; then
    echo "Starting Release..."
    cd $LOCAL && python3 -O ./adpio_edge.py
elif [[ "$DEBUG" == "build" ]]; then
    echo "Starting Build..."
else
    echo "Starting Debug..."
    cd $LOCAL && python3 ./adpio_edge.py
fi
