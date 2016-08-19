#!/bin/bash
#############################################################
usage1="Usage: $0 filename [xgraph-options]"
#############################################################
if [  $# -lt 1 ] ;  then
    echo $usage1
    exit 1
fi
file=$1
shift
echo \"U-Mom > res.plot
grep "R: " $file | grep -v ERROR | awk ' { print 1+i++,$4}'  >> res.plot
echo "   "   >>  res.plot
echo \"V-Mom >>  res.plot
grep "R: " $file |grep -v ERROR |  awk ' { print 1+i++,$5}'  >> res.plot
echo "   "   >>  res.plot
echo \"W-Mom >>  res.plot
grep "R: " $file |grep -v ERROR |  awk ' { print 1+i++,$6}'  >> res.plot
echo "   "   >>  res.plot
echo \"P-Prime >>  res.plot
grep "R: " $file |grep -v ERROR |  awk ' { print 1+i++,$7}'  >> res.plot
echo "   "   >>  res.plot
echo \"Turb_k >>  res.plot
grep "R: " $file |grep -v ERROR |  awk ' { print 1+i++,$8}'  >> res.plot
echo "   "   >>  res.plot
echo \"Turb_w >>  res.plot
grep "R: " $file |grep -v ERROR |  awk ' { print 1+i++,$9}'  >> res.plot
echo "   "   >>  res.plot
#


cat res.plot | xgraph  -lw 2 -lny -fmty "%6.1e" -t "...`pwd | tail -55c`"  $@
