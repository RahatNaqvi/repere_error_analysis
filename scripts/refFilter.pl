#!/usr/bin/perl
use strict;

while(<>){
	chomp;
	my @a = split;
	
	if (($a[4] !~ m/speaker#/i) && ($a[4] !~ m/^Inconnu_/i) && ($a[4] !~ m/_BFM/i)&& ($a[4] !~ m/_LCP/i))  {
		print "$a[0] $a[1] $a[2] $a[4]\n";
	}
}