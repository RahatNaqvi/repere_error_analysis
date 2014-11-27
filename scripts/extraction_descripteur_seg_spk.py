from pyannote.parser import MagicParser
import numpy

if __name__ == '__main__':

    parser_spk = MagicParser().read('../reference/test2.repere')

    fout_spkshow = open('../spkshow/data/descripteur_prediction/test2.spkshow.seg', 'w')
    fout_spkseg = open('../spkseg/data/descripteur_prediction/test2.spkseg.seg', 'w')

    for show in parser_spk.uris:
        list_spk = {}

        spk = parser_spk(uri=show, modality="speaker")
        for segment, track, label in spk.itertracks(label=True):
            if type(label).__name__ != 'Unknown' and 'BFMTV_' not in label and 'LCP_' not in label :
                list_spk.setdefault(show+'#'+label, {'seg':[], 'dur':[]})
                list_spk[show+'#'+label]['dur'].append(segment.duration)
                list_spk[show+'#'+label]['seg'].append(segment)

        for spk in sorted(list_spk):

            l_overlap_spkshow = []
            for seg in sorted(list_spk[spk]['seg']):
                l_overlap = []
                for spk2 in list_spk:
                    if spk != spk2:
                        for seg2 in list_spk[spk2]['seg']:
                            if seg & seg2:
                                l_overlap.append((seg & seg2).duration)
                                l_overlap_spkshow.append((seg & seg2).duration)
                fout_spkseg.write(spk.split('#')[0]+' '+str(seg.start)+' '+str(seg.end)+' '+spk.split('#')[1])
                fout_spkseg.write(' '+str(seg.duration))
                fout_spkseg.write(' '+str(numpy.sum(l_overlap))+' '+str(len(l_overlap)))
                fout_spkseg.write(' '+str(numpy.sum(list_spk[spk]['dur']))+' '+str(numpy.mean(list_spk[spk]['dur']))+' '+str(len(list_spk[spk]['dur'])))
                fout_spkseg.write('\n')

            fout_spkshow.write(spk)
            fout_spkshow.write(' '+str(numpy.sum(list_spk[spk]['dur']))+' '+str(numpy.mean(list_spk[spk]['dur']))+' '+str(len(list_spk[spk]['dur'])))
            fout_spkshow.write(' '+str(numpy.sum(l_overlap_spkshow))+' '+str(len(l_overlap_spkshow)))
            fout_spkshow.write('\n')                