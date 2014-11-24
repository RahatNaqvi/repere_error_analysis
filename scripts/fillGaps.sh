#!/bin/bash

# Fill intra-speaker gaps shorter than given duration (default 0.5 sec)
# Syntax :
# fillGaps.sh [0.5] < repere_hypothesis > filtered_hypothesis

# REPERE format:
#   showID startTime(sec) endTime(sec) "speaker" speakerName

gap=${1:-"0.5"}

sort -k 1,1 -k 2,3n -k5,5 | awk -v gap=$gap '
  BEGIN {
    showID = ""; startTime = 0; endTime = 0; speakerName = "";
  }
  $4 == "speaker" {
    if (showID == $1 && speakerName == $5 && endTime + gap >= $2) {
      endTime = $3
    } else {
      if (showID != "") print showID, startTime, endTime, "speaker", speakerName;
      showID = $1;
      startTime = $2;
      endTime = $3;
      speakerName = $5;
    }
  }
  END {
    print showID, startTime, endTime, "speaker", speakerName;
  }'
