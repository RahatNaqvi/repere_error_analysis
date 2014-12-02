#!/usr/bin/perl
#
# trs2mdtm -- parse transcriber file to create reference speaker
# clustering MDTM file.
#
# Guillaume Gravier [ggravier@irisa.fr], Dec 2004.
#

# Create a reference diarization file (MDTM) from the specified
# transcriber files.

use Getopt::Long;

#
# options
#
my $scpfn = undef;
my $uemfn = undef;

my $ofn = "-";

my $trace = 0;
my $help = 0;

my %topics = ();
my %speakers = ();
my @sec = ();
my @turn = ();
my @bg = ();

my $eps = 0.001;

#
# Process command line
#
Getopt::Long::config("no_ignore_case");
GetOptions(
		 "list|i=s" => \$scpfn,
		 "exclude|x=s" => \$uemfn,
		 "output|o=s" => \$ofn,
					 "verbose|v" => \$trace,
					 "help|h" => \$help
					)
	or usage();

usage() if $help;

my @trsfn = @ARGV;
push @trsfn, load_file_list($scpfn) if defined $scpfn;

#
# Load exclude regions
#
my @uem = ();
@uem = uemread($uemfn) if defined $uemfn;

foreach my $ifn (@trsfn) {
	%topics = ();			# list of topics per source
	%speakers = ();		# list of speakers per source
	@sec = ();				 # table of sections
	@turn = ();				# table of turns
	@bg = ();					# table of background events

	$ifn =~ /((?:.*\/)*)([^\/\.]+)(?:\.([^\/\.]))?/;
	my $source = $2;
	load_trans_file($ifn);

	print "	 source=$source\n" if $trace;

	my @segTmp = ();
	my @seg = ();
	my $iseg = 0;
	my $prev=$turn[0]->{start_time};
	foreach (@turn) {
		#next if not defined $_->{speakers};
		my $label = join "+", sort {$a cmp $b} split /\s+/, $_->{speakers};
		#printf STDERR "$label $_->{speakers}\n";
		
#		if ($iseg > 0 and $seg[$iseg-1]->{label} eq $label and abs($seg[$iseg-1]->{end_time} - $_->{start_time}) < $eps) {
#			$seg[$iseg-1]->{end_time} = $_->{end_time};
#		}
#		else {
			if($label eq "") {
				$label="empty";
			}
			
			if(($_->{start_time} - $prev) > 0){
				$seg[$iseg]->{label} = "hole";
				$seg[$iseg]->{start_time} = $prev;
				$seg[$iseg++]->{end_time} = $_->{start_time};
				
				printf STDERR "%f %f %s\n", $seg[$iseg-1]->{start_time}, $seg[$iseg-1]->{end_time}, $seg[$iseg-1]->{label};
			}
			
			$seg[$iseg]->{label} = $label;
			$seg[$iseg]->{start_time} = $_->{start_time};
			$seg[$iseg++]->{end_time} = $_->{end_time};
			$prev=$_->{end_time};
			
			
#		}
	}




	# we have a segmentation. If target exclude regions were
	# specified, it's time to do the job....
	if (defined $uemfn) {
		my @sil = sort {$a->{start_time} <=> $b->{start_time}} grep $_->{filename} eq $source, @uem;
		@seg = discard(\@seg, \@sil);
	}

	my @segInfo=();
	my $segInfoNb = 0;
	open(F, ">>$ofn") or die "cannot open output file $ofn\n";
	foreach (@seg) {
		
		my $st = $_->{start_time};
		my $e = $_->{end_time};
		
		my $type = "speaker";
		my $name = $_->{label};
		foreach (split /\+/, $_->{label}) {
			my $type = "noise";
			my $name=$_;
			if(defined $speakers{$_}{name}) {
				$type = "speaker";
				$name = $speakers{$_}{name};
			}
			#printf F "%s %.3f %.3f %s %s\n", $source, $st, $e, $type, $name;
			
			$segInfo[$segInfoNb]->{start}=$st;
			$segInfo[$segInfoNb]->{end}=$e;
			$segInfo[$segInfoNb]->{source}=$source;
			$segInfo[$segInfoNb]->{type}=$type;
			$segInfo[$segInfoNb++]->{name}=$name;
		}
		
	}
	
	for(my $i=0; $i < scalar(@segInfo); $i++) {
		if( $segInfo[$i]->{name} ne "delete") {
			for(my $j=$i+1; $j < scalar(@segInfo); $j++) {
				if(($segInfo[$i]->{name} eq $segInfo[$j]->{name}) && ($segInfo[$i]->{end} == $segInfo[$j]->{start})) {
					$segInfo[$i]->{end} = $segInfo[$j]->{end};
					$segInfo[$j]->{name} = "delete";
				}
			}
		}
	}
	
	@seg=();
	foreach $w (@segInfo) {
		if($w->{type} ne "noise") {
			push @seg, $w;
		} 
	}
	
	for(my $i=0; $i < scalar(@seg)-1; $i++) {
		my $d = $seg[$i+1]->{start} - $seg[$i]->{end};
		if (($d < 1) && ($seg[$i]->{name} eq $seg[$i+1]->{name})){
			$seg[$i+1]->{name} = "delete";
			$seg[$i]->{end} = $seg[$i+1]->{end};
		}
	}
	
	for(my $i=0; $i < scalar(@seg); $i++) {
		if($seg[$i]->{name} ne "delete") {
			printf "%s %.3f %.3f %s %s\n", $seg[$i]->{source}, $seg[$i]->{start}, $seg[$i]->{end}, $seg[$i]->{type}, $seg[$i]->{name};
			$prev=$seg[$i]->{end};
		}
	}
	
	close(F);
}

0;

sub findName() {
	my $src = shift;
	my $name = shift;
	
	my @lst = split(/\+/, $src);
	my $res="";
	
	for(my $i = 0; $i < scalar(@lst); $i++) {
#		printf STDERR "$lst[$i] eq $name\n";
		if($lst[$i] eq $name) {
			$lst[$i]="";
		} else {
			if($res ne "") {
				$res.="+".$lst[$i];
			} else {
				$res=$lst[$i];
			}
		}
	}
	return res;
}

# ------------------------- #
# ----- sub discard() ----- #
# ------------------------- #
#
# Discard silence regions from target regions
#
sub discard(**) {
	my $seg1 = shift;
	my $seg2 = shift;
	my @oseg = ();
	my $n = 0;

	my $i2 = 0;
	my $n2 = $#$seg2;

	for my $i1 (0 .. $#$seg1) {

		$i2++ while $i2 < $n2 and $$seg2[$i2]->{end_time} < $$seg1[$i1]->{start_time};

		if ($$seg2[$i2]->{end_time} < $$seg1[$i1]->{start_time} or $$seg2[$i2]->{start_time} > $$seg1[$i1]->{end_time}) {
			$oseg[$n]->{label} = $$seg1[$i1]->{label};
			$oseg[$n]->{start_time} = $$seg1[$i1]->{start_time};
			$oseg[$n++]->{end_time} = $$seg1[$i1]->{end_time};
		}
		else {
			my ($a, $b, $overlap) = undef;

			$a = $$seg1[$i1]->{start_time};

			while ($a != $$seg1[$i1]->{end_time}) {

	if ($i2 <= $n2 and $$seg2[$i2]->{start_time} <= $a) {
		if ($$seg2[$i2]->{end_time} < $$seg1[$i1]->{end_time}) {
			$b = $$seg2[$i2]->{end_time};
			$i2++;
		}
		else {
			$b = $$seg1[$i1]->{end_time};
		}
	}
	else {
		if ($i2 <= $n2 and $$seg2[$i2]->{start_time} < $$seg1[$i1]->{end_time}) {
			$b = $$seg2[$i2]->{start_time};
		}
		else {
			$b = $$seg1[$i1]->{end_time};
		}

		$oseg[$n]->{label} = $$seg1[$i1]->{label};
		$oseg[$n]->{start_time} = $a;
		$oseg[$n++]->{end_time} = $b;
	}
	
	$a = $b;
			}
		}
	}

	return @oseg;
}

# ------------------------- #
# ----- sub uemread() ----- #
# ------------------------- #
#
# Read exclude regions from UEM. Sort the resulting table by event,
# document and start time.
#
sub uemread($) {
	my $fn = shift;
	my @tab = ();
	my $n = 0;

	open(F, $fn) or die "cannot open uem file $fn\n";

	foreach ( <F> ) {
		chomp;

		s/;.*//g; s/^\s*//; s/\s*$//;
		next if /^\s*$/;

		/^([^\s]+)\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)$/;

		my $seg = undef;
		$seg->{filename} = $1;
		$seg->{channel} = $2;
		$seg->{start_time} = $3;
		$seg->{end_time} = $4;

		push @tab, $seg;
	}

	close(F);

	return @tab;
}

# -------------------------------- #
# ----- sub load_file_list() ----- #
# -------------------------------- #
#
# Load list fo files from file.
#
sub load_file_list($) {
	my $fn = shift;
	my @tab = ();

	open(F, $fn) or die "cannot open file list $fn\n";

	foreach ( <F> ) {
		chomp;
		push @tab, $_;
	}
	close(F);

	return @tab;
}

# --------------------------------- #
# ----- sub load_trans_file() ----- #
# --------------------------------- #
#
# Load lots of usefull information from the transcriber file. Note
# that the parsing routine below is *not* an XML parser but rather a
# dirty hack exploiting the structure of transcriber files and, in
# particular, the fact that a line contains no more than one tag.
#
sub load_trans_file($) {
	my $fn = shift;

	open(F, $fn) or die "cannot open file $fn\n";

	/((?:.*\/)*)([^\/\.]+)(?:\.([^\/\.]))?/;
	my $source = $2;

	my @state = ("<root>");
	my $line = 0;

	my ($nsecs, $nturns, $nbgs) = 0;

	foreach ( <F> ) {
		chomp;
		$line += 1;

		if (/<(.+)>/) { # we have a tag
			$1 =~ /([\/\?!]?)([^\s]+)(\s+\w+=\".*\")*(\/?)/; 
	
			my $tag_type = undef;
			my $open = $1;
			my $instant = $4;
			my $tag = $2;
			my $attributes = $3;
	
			if (defined $open and $open =~ /\//) {
				$tag_type = "close_tag";
			}
			elsif (defined $instant and $instant =~ /\//) {
				$tag_type = "instant_tag";
			}
			elsif ($open =~ /^$/ and $instant =~ /^$/) {
				$tag_type = "open_tag";
				push @state, $tag;
			}

			next if not defined $tag_type;

			# >>>>> Topics <<<<<
			if ($tag =~ /^topic$/i) {
				my ($id, $desc) = undef;

				die "<Topic> tag out of <Topics> at line $line in $source\n" if $state[$#state] !~ /^topics$/i;
	
				$id = $1 if $attributes =~ /id=\"([^\"]*)\"/;
				$desc = $1 if $attributes =~ /desc=\"([^\"]*)\"/;
	
				$desc =~ tr/[A-ZÉ ]/[a-zé_]/;
				$topics{$id} = $desc;
			}
	
			# >>>>> Speakers <<<<<
			elsif ($tag =~ /^speaker$/i) {
				my ($id, $name, $type, $dialect, $scope) = undef;
			
				die "<Speaker> tag out of <Speakers> at line $line in $source\n" if $state[$#state] !~ /^speakers$/i;
				
				$id = $1 if $attributes =~ /id=\"([^\"]*)\"/;
				$name = $1 if $attributes =~ /name=\"([^\"]*)\"/;
				$type = $1 if $attributes =~ /type=\"([^\"]*)\"/;
				$dialect = $1 if $attributes =~ /dialect=\"([^\"]*)\"/;
				$scope = $1 if $attributes =~ /scope=\"([^\"]*)\"/;
			
				# print STDERR "id=$id	 name=$name	 type=$type";
				# hack name
				$name =~ s/[,:].*$//g;
				$name =~ s/\s+/_/;
				$name =~ s/(^_|_$)//;
			
				#$name = join("_", $source, $name) unless $scope eq "global";
			
							# print STDERR " --> $name\n";
			
				$speakers{$id}{name} = $name;
				$speakers{$id}{type} = $type;
				$speakers{$id}{dialect} = $dialect;
			}
	
			# >>>>> Sections <<<<<
			elsif ($tag =~ /^section$/i and $tag_type =~ /open_tag/) {
				my ($st, $et, $type, $id) = undef;
			
				die "<Section> tag out of <Episode> at line $line in $source\n" if $state[$#state-1] !~ /^episode$/i;
			
				$st = $1 if $attributes =~ /startTime=\"([^\"]*)\"/;
				$et = $1 if $attributes =~ /endTime=\"([^\"]*)\"/;
				$type = $1 if $attributes =~ /type=\"([^\"]*)\"/;
				$id = $1 if $attributes =~ /topic=\"([^\"]*)\"/;
			
				my $x = undef;
			
				$x->{start_time} = $st;
				$x->{end_time} = $et;
				$x->{type} = $type;
				$x->{topic} = $id;
				
				#printf STDERR "$nsecs $type $st\n";

				push @sec, $x;
				$nsecs++;
			}
	
			# >>>>> Turn <<<<<
			elsif ($tag =~ /^turn$/i and $tag_type =~ /open_tag/) {
				my ($st, $et, $id) = undef;
			
				die "<Turn> tag out of <Section> at line $line in $source\n" if $state[$#state-1] !~ /^section$/i;	
			
				$st = $1 if $attributes =~ /startTime=\"([^\"]*)\"/;
				$et = $1 if $attributes =~ /endTime=\"([^\"]*)\"/;
				$id = $1 if $attributes =~ /speaker=\"([^\"]*)\"/;
				
				my $x;
			
				$x->{start_time} = $st;
				$x->{end_time} = $et;
				$x->{speakers} = $id;
				
				my $secType = $sec[$nsecs-1]->{type};
				if($secType eq "nontrans") {
					$x->{speakers} = "nontrans";
				}
				
				push @turn, $x;
				$nturns++;
			}
			elsif ($tag =~ /^event$/i ) {
				my ($desc, $type, $extent) = undef;
			
				
#				printf STDERR "$nsecs $secType\n";
				
				$desc = $1 if $attributes =~ /desc=\"([^\"]*)\"/;
				$type = $1 if $attributes =~ /type=\"([^\"]*)\"/;
				$extent = $1 if $attributes =~ /extent=\"([^\"]*)\"/;
				
				my $x = pop @turn;
				if ((not defined $x->{speakers}) || ($x->{speakers} eq "")) {
				#printf STDERR "Event found $desc $type $extent \n";
					$x->{speakers} = $desc."__".$type; 
				} 
				push @turn, $x;
				
			}
			# >>>>> Background <<<<<
			elsif ($tag =~ /^background$/i) {
				my ($t, $type, $level) = undef;
			
				$t = $1 if $attributes =~ /time=\"([^\"]*)\"/;
				$type = $1 if $attributes =~ /type=\"([^\"]*)\"/;
				$level = $1 if $attributes =~ /level=\"([^\"]*)\"/;
				
				# When a background tag is found, it ends the previous
				# background tag if the latter has not already been
				# ended. If level is off, then it's only the end. Otherwise,
				# it's the start of a new background tag (whether the types
				# match or not)... A tag has been ended if duration has been
				# specified to a positive value.
				
				$bg[$#bg]->{end_time} = $t if $#bg != -1 and $bg[$#bg]->{end_time} < 0;
				# $bg[$#bg]->{duration} = $t - $bg[$#bg]->{start_time} if $#bg != -1 and $bg[$#bg]->{duration} < 0;
				
				if ($level !~ /off/) {
					my $x;
			
					$x->{start_time} = $t;
					$x->{id} = $type;
					$x->{level} = $level;
					$x->{end_time} = -1;
					# $x->{duration} = -1;
					push @bg, $x;
					$nbgs++;
				}
				elsif ($#bg != -1) {
					$bg[$#bg]->{end_time} = $t;
					# $bg[$#bg]->{duration} = $t - $bg[$#bg]->{start_time};
				}
			}

			# >>>>> Sync <<<<<
			elsif ($tag =~ /^sync$/i) {
				die "<Sync> tag out of <Turn> at line $line in $source\n" if $state[$#state] !~ /^turn$/i;
			}
			pop @state if $tag_type =~ /close_tag/;
		}
	}

	close(F);

	my $dur = $sec[$#sec]->{start_time} + $sec[$#sec]->{duration};

	printf "	%-30s	%5d sections, %5d turns, %5d background segments	[%d topics / %d speakers] (T=%.2f)\n",
			$source, $nsecs, $nturns, $nbgs, scalar keys %topics, scalar keys %speakers, $dur / 60.0 if $trace;
}

# ----------------------- #
# ----- sub usage() ----- #
# ----------------------- #
sub usage() {
print <<EOF;
Usage:
	trs2mdtm [options] trsfn ...

Synopsis:
	Generate reference diarization MDTM file.

Options:
	-i, --list=fn							process transcriber files listed in <fn>.
	-x, --exclude=fn					 exclude regions from target events

	-o, --output=fn						output filename

	-v, --verbose							trace
	-h, --help								 this help message
EOF
exit 0;
}
