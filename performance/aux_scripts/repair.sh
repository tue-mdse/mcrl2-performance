#!/bin/bash
for F in `find ./data -name *.perf -or -name *.mem` ; do
  sed -i -e "s/^-1/4982/" $F
done
