from pyannote.parser import MagicParser

if __name__ == '__main__':
    parser = MagicParser().read('../reference/test2.repere')
    fout_spkseg = open('../reference/list_spkseg', 'w')
    fout_spkshow = open('../reference/list_spkshow', 'w')
    list_spkshow = set([])
    for show in parser.uris:
        annotation = parser(uri=show, modality="speaker")
        for segment, track, label in annotation.itertracks(label=True):
            if type(label).__name__ != 'Unknown' and 'BFMTV_' not in label and 'LCP_' not in label :
                fout_spkseg.write(show+" "+str(segment.start)+" "+str(segment.end)+" "+label+'\n')
                list_spkshow.add(show+'#'+label)

    for spk in sorted(list_spkshow):
        fout_spkshow.write(spk+'\n')
