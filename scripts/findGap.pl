#!/usr/bin/perl
use strict;

my $prev=0;
my $name="";

while(<>) {
	chomp;
	my @a=split;
	my $d = $a[1]-$prev;
	if(($name eq $a[4]) && ($d > 0.001)){
		print "$a[0] $prev $a[1] hole hole\n";
	}
	$prev=$a[2];
	$name=$a[4];
}