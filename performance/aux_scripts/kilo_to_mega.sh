#!/bin/bash
for f in `find . -name *.mem` ; do
  v=`grep 4360 $f | sed -e "s/4360\t//"`
  if [ "$v" -ge "0" ] ; then
    w=`echo "scale = 2; $v / 1024" | bc | sed -e "s/^\./0./"`
    sed -i -e "s/4360\t$v/4360\t$w/" $f
  #else
  #  w=$v
  fi
  #echo "$f: $v -> $w"
done
