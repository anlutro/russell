#!/usr/bin/env sh

tests=''

for file in tests/*.py; do
	tests="$tests $file"
done

python3 -m unittest $tests

