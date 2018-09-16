#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

find $1 -name "*.md" -type f -exec python3 ${DIR}/check_file.py {} \+
