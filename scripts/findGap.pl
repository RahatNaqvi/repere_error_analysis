#!/usr/bin/perl
use strict;

my $prev=0;
my $show="";
my $name="";

open(REF, "$ARGV[0]")or die "impossible $ARGV[0] $!";
my %gap=();

while(<REF>) {
	chomp;
	my @a=split;
	my $d = $a[1]-$prev;
	if(($show eq $a[0]) &&($name eq $a[4]) && ($d > 0.001)){
		$gap{$a[0]}{$prev}=$a[1];
		#print "$a[0] $prev $a[1] hole hole\n";
	}
	$show=$a[0];
	$prev=$a[2];
	$name=$a[4];
}

close(REF);

open(HYP, "$ARGV[1]")or die "impossible 2 $ARGV[1] $!";
my @seg=();
my $nb=0;
while(<HYP>) {
	chomp;
	my @a=split;
	if($a[3] eq "speaker") {
		push(@seg, [@a]);
	}
}
close(HYP);

for(my $i=0; $i < scalar(@seg); $i++) {
	#printf STDERR $seg[$i][0]."\n";
	while( my ($s,$e) = each(%{$gap{$seg[$i][0]}}) ) {
		#printf STDERR "Clef=$s Valeur=$e\n";
		if(($s > $seg[$i][1]) && ($e < $seg[$i][2])) {
			#printf STDERR "$seg[$i][0] $s $e\n";
			
			my @b=@{$seg[$i]};
			$b[1]=($s+$e)/2;
			push(@seg, [@b]);
			$seg[$i][2]=($s+$e)/2;
			
			#printf STDERR "seg1 $seg[$i][0] $seg[$i][1] $seg[$i][2] $seg[$i][3]\n";
			#printf STDERR "seg2 $b[0] $b[1] $b[2] $b[3]\n";
		}
	}
}

for(my $i=0; $i < scalar(@seg); $i++) {
	print "$seg[$i][0] $seg[$i][1] $seg[$i][2] $seg[$i][3] $seg[$i][4]\n";
}
