#!/bin/bash

score=../evalSegHB/PERCOOL_sup.repere.evalsegHB

for i in `cut -d" " -f 1 $score | sort -u`; do
	grep $i $score | awk '{s=$2*100; d=($3-$2)*100; print $1" 1 "s" "d" U U U "$4;}' > refSEG/$i.seg
	../../scripts/ctm+seg2stm4inl.pl refSEG/$i.seg hypCTM/$i.bck > hypSTM/$i.txt
done


cat hypSTM/*.txt | awk '{print $4";"$5";"$6";"$7";"$8";"$9";"$10";"$11;}' > stat.csv