#!/usr/bin/perl

use strict;

my %dic=();

while(<>) {
	chomp;
	my @a = split;
	$dic{$a[7]}{$a[0]} += $a[3];
}

#print ";;Spk nbSessionREPERE dureeSessionREPERE nbSessionAutre dureeAutre\n";
print ";; locuteur dureedapprentissageGlobal nbdesessionsdapprentissageGlobal dureedapprentissageRepere nbdesessionsdapprentissageRepere dureedapprentissageAutre nbdesessionsdapprentissageAutre\n";

foreach my $spk (keys %dic) {
	my $nbShowEx = 0;
	my $nbShowIn = 0;
	my $dIn = 0;
	my $dEx = 0;
	foreach my $show (keys %{$dic{$spk}}) {
		if($show =~ m/^[A-Z]/) {
			$nbShowIn++;
			$dIn += $dic{$spk}{$show};
		} else {
			$nbShowEx++;
			$dEx += $dic{$spk}{$show};
		}
		
	}
	$dIn /= 100;
	$dEx /= 100;
#	if(($dIn > 0) && ($dEx > 0)) {
#		print "$spk $nbShowIn $dIn $nbShowEx $dEx\n";
#	} else {
		my $nbShowInTot = $nbShowIn+$nbShowEx;
		my $dTot = $dIn + $dEx;
		print "$spk $dTot $nbShowInTot $dIn $nbShowIn $dEx $nbShowEx\n";
#	}
}

