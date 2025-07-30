#!/bin/bash

#sed 's/^[0-9.]*\([^0-9]*\)\([0-9]*\), "\([^”]*\)"\([^,]*\)\([^,]*\)/\1/g' $1
# Byron's format
#sed 's/,”/”/g' $1 |sed 's/^[0-9. ]*\t\([^0-9]*\)\([0-9]*\), “\([^”]*\)”[ \t]*\([^,]*\),[ \t]*\([^,.]*\)[.,]\([^$]*\)/@misc{key,\n\tauthor={\1},\n\tyear={\2},\n\ttitle={\3},\n\taddress={\4,\6},\n\tmonth={\5}}\n/g'
# Laurel's format
sed 's/^\([^\t]*\)\t\([^\t]*\)\t\([^\t]*\)\t\t\t\t\([^\t]*\)\t\([^\t]*\)/@misc{key,\n\tauthor={\1},\n\tyear={\4},\n\ttitle={\2},\n\taddress={\4 \5},\n\tmonth={\5}}\n/g' $1