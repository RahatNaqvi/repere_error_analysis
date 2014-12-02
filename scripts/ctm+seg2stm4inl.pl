#!/usr/bin/perl -w
use strict;
use locale;
use POSIX qw(locale_h);
setlocale(LC_CTYPE,"fr_FR.ISO8859-1"); # Yannick, LIUM 

if ($#ARGV!=1) {
  print STDERR "Usage: $0 seg ctm > out\n";
  exit;
}

open (FSEG, "$ARGV[0]") || die "can't open $ARGV[0]\n";
open (FCTM, "$ARGV[1]") || die "can't open $ARGV[1]\n";

my @iSeg=();
my @dSeg=();
my @fSeg=();
my @lSeg=();
#$first=1;
my $chan = 0;
my $gender = "empty";
my $nbSeg=0;
while (<FSEG>) {
	if ( (/^;;/)) {
		next;
	}

	my @item = split;
	if($item[5] eq 'S') {
		$chan='f0';
	} else {
		$chan='f3';
	}
	
	if($item[4] eq 'M') {
		$gender='male';
	} else {
		$gender='female';
	}
		
	my $infoSeg="$item[0] " . ($item[2]/100) . " " . (($item[2]+$item[3])/100). " $item[7] ";

	$iSeg[$nbSeg] = $infoSeg;
	$dSeg[$nbSeg] = $item[2]/100;
	$fSeg[$nbSeg] = ($item[2]+$item[3])/100;
	$lSeg[$nbSeg] = $item[3]/100;
	$nbSeg++;
}

my $nbCTM = 0;
my @ctmStart = ();
my @ctmEnd = ();
my @ctmMid = ();
my @ctmLen = ();
my @ctmWord = ();

while (<FCTM>) {
	my @item = split;
	$ctmStart[$nbCTM] = $item[2];
	$ctmLen[$nbCTM] = $item[3];
	$ctmEnd[$nbCTM] = $item[2] + $item[3];
	$ctmMid[$nbCTM] = $item[2] + $item[3]/2.0;
	$ctmWord[$nbCTM] = $item[4];
	$nbCTM++;
}

for(my $i=0; $i < $nbSeg; $i++) {
    my $ch = "";
    my $start = $dSeg[$i];
    my $end = $fSeg[$i];
    my $len = $lSeg[$i];
    my $head = $iSeg[$i];
    my $lenNSP = 0;
    my $lenWord = 0;
    my $nWord = 0;
    my $nNSP= 0;
    
    for(my $j=0; $j < $nbCTM; $j++) {
		my $mid = $ctmMid[$j];
		if (($mid >= $start ) && ($mid <= $end)) {
			my $s=$start;
			if($start < $ctmStart[$j]) {
				$s=$ctmStart[$j];
			}
			my $e = $end;
			if($end > $ctmEnd[$j]) {
				$e=$ctmEnd[$j];
			}
			my $l=$e-$s;
	    	if($ctmWord[$j]=~ m/<.+>|\[.+\]|euh/) {
				if(($ctmWord[$j] ne "<s>")&&($ctmWord[$j] ne "</s>")){
					#print STDERR "filler: ".$ctmWord[$j]."\n";
					
					$lenNSP += $l;
					$nNSP++;
				}
	    	} else {
				$ch .= $ctmWord[$j]." ";
				$lenWord += $l;
				$nWord++;
	    	}
		}
    }
    my $rlen = $lenNSP/$len;
    my $r = 0;
    if (($nWord+$nNSP) > 0){
    	$r=$nNSP/($nWord+$nNSP);
    }
#    if (($r > 0.85) || ($ch eq "")) {
#	print "REMOVE $i | $lenNSP | $len $start | $r ** $head $ch\n";
#    } else {
#		if ($ch ne "") {
	print "$head $nWord $nNSP $len $lenWord $lenNSP $r $rlen $ch\n";
#		}
#   }
}
