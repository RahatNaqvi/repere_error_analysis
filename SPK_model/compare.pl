#!/usr/bin/perl

use strict;
use File::Basename;

my %dic=();

sub readData {
	my $sys = shift;
	my $fn = "$sys/$sys.lst";
	if ( ! -e $fn) {
		print "le fichier $fn n'existe pas\n";
	}
	if ( ! open(FIC, "$fn")) {
		print "le fichier $fn n'est pas ouvert\n";
	}
	
	my @stat=();
	my $nb = 0;
	
	while(<FIC>) {
		chomp;
		my @a = split;
		#print "$sys $a[0]\n";
		
		if($a[0] ne ";;") {
			$dic{$a[0]}{$sys}=@a;
			for(my $i=1; $i < scalar(@a); $i++) {
				$stat[$i-1]+=$a[$i];
			}
			$nb++;
		}
	}

	printf "%10s", "$sys ";
	foreach my $v (@stat) {
		my $p = $v / $nb;
		printf "%15.2f ", $p;
	}
	print "\n";
	close(FIC);
}

printf "%10s %15s %15s %15s %15s %15s %15s ", "systeme","dureeGlobal","nbSessionGlobal","dureeRepere","nbSessionRepere","dureeAutre","nbSessionAutre\n";
foreach my $arg (@ARGV) {
	readData($arg);
}
print "-----------------------------------------------\n";

my @commun = ();

foreach my $name (keys %dic) {
	my $nb;
	foreach my $sys (keys %{$dic{$name}}) {
		$nb++;
	}
	$commun[$nb]++;
	#print "$name $nb\n";
}

for(my $k=1; $k < scalar(@commun); $k++) {
	print "locuteur commun à $k systemes : $commun[$k]\n";
}

