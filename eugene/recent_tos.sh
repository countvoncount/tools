#!/bin/bash

set -xe

SIDS="$1"

# SID 100 is misbehaving...
if [ -z "$SIDS" ];
then
    SIDS="26 28 40 123 198 264 315 367 431 436 554 570 606 612 701 748 795 853 883 982 1072 1091 1109 1140 1156 1200 1207 1237 1242 1243 1415"
    #SIDS="26 28 198 570 883 1415"
fi

[ -z "$NDAYS" ] && NDAYS=120

for sid in $SIDS
do
    nice bash ./sync.sh "$sid"
done


for sid in $SIDS
do
    nice ./dbdata.py -s $sid -n $NDAYS > SS_`printf "%05d" "${sid}"`.csv
done






