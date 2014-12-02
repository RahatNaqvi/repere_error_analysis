for i in trs/*.trs; do 
    ../scripts/trs2ref.pl $i ; 
done > test2.repere.v2

../scripts/refFilter.pl test2.repere.v2 list_spkseg.v2