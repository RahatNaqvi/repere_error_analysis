
for hyp in PERCOL_PERFIDE_PRIMARY.hyp QCOMPERE_Qcoccinelle_primary.hyp SODA_mono.hyp; do
	for ref in ../reference/test2.repere.noise.*.v2; do
		echo $hyp $ref
		gap=`basename $ref | cut -d"." -f 4,5`
				b=`basename $hyp .hyp`
		../scripts/findGap.pl $ref $hyp $gap | grep " speaker " | sort -k1,1 -k2,2n > $b.$gap.hyp
		#echo $gap $b
	done
done
