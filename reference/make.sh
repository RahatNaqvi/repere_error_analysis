
for m in 0.5 1.0 1.5 2.0 3.0; do
	for i in trs/*.trs; do 
		../scripts/trs2ref.pl -g $m $i ; 
	done > test2.repere.$m.v2 2> test2.repere.noise.$m.v2
	../scripts/refFilter.pl test2.repere.$m.v2 > list_spkseg.$m.v2
done