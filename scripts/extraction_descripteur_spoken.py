from pyannote.parser import MagicParser
import numpy
from itertools import tee, islice, chain, izip

if __name__ == '__main__':

    #parser_spk = MagicParser().read('../reference/test2.repere')
    parser_spk = MagicParser().read('../reference/test2.1.0.v2.repere')
    parser_spo = MagicParser().read('../reference/test2.spoken.repere')

    fout_spkshow = open('../spkshow/data/descripteur_prediction/test2.spkshow.spoken', 'w')
    fout_spkseg = open('../spkseg/data/descripteur_prediction/test2.spkseg.spoken', 'w')

    for show in parser_spo.uris:
        spo = parser_spo(uri=show, modality="spoken")
        spk = parser_spk(uri=show, modality="speaker")

        list_spk = {}
        l_st_previous_next = {}
        for segment, track, label in spk.itertracks(label=True):
            if type(label).__name__ != 'Unknown' and 'BFMTV_' not in label and 'LCP_' not in label :
                list_spk.setdefault(show+'#'+label, {'speech':[], 'spo':[]})
                list_spk[show+'#'+label]['speech'].append(segment)

            l_st_previous_next[segment] = {'previous':False, 'next':False}
            for segment2, track2, label2 in spk.itertracks(label=True):
                if track2 != track:
                    if segment2.start < segment.start:
                        if l_st_previous_next[segment]['previous']:
                            if segment2.start > l_st_previous_next[segment]['previous'].start:
                                l_st_previous_next[segment]['previous'] = segment2    
                        else:
                            l_st_previous_next[segment]['previous'] = segment2
                    if segment2.end > segment.end:
                        if l_st_previous_next[segment]['next']:
                            if l_st_previous_next[segment]['next'].end > segment2.end:
                                l_st_previous_next[segment]['next'] = segment2    
                        else:
                            l_st_previous_next[segment]['next'] = segment2

        for segment, track, label in spo.itertracks(label=True):
            if show+'#'+label in list_spk:
                list_spk[show+'#'+label]['spo'].append(segment)

        for spk in sorted(list_spk):
            #spkshow
            spo_current_st_show = 0
            spo_previous_st_show = 0
            spo_next_st_show = 0
            spo_other_st_show = 0


            for seg_spo in list_spk[spk]['spo']:
                spo_used = False
                for seg_spk in list_spk[spk]['speech']:
                    if seg_spk & seg_spo:
                        spo_current_st_show+=1
                        spo_used=True
                    elif l_st_previous_next[seg_spk]['previous'] and seg_spo & l_st_previous_next[seg_spk]['previous']:
                        spo_previous_st_show+=1
                        spo_used=True
                    elif l_st_previous_next[seg_spk]['next'] and seg_spo & l_st_previous_next[seg_spk]['next']:
                        spo_next_st_show+=1
                        spo_used=True
                if not spo_used:
                    spo_other_st_show+=1

            
            fout_spkshow.write(spk)
            fout_spkshow.write(' '+str(spo_previous_st_show)+' '+str(spo_current_st_show)+' '+str(spo_next_st_show)+' '+str(spo_other_st_show))
            fout_spkshow.write('\n')
            
            
            #spkseg
            for seg_spk in list_spk[spk]['speech']:
                spo_current_st = 0
                spo_previous_st = 0
                spo_next_st = 0                
                for seg_spo in list_spk[spk]['spo']:
                    if seg_spk & seg_spo:
                        spo_current_st+=1
                    elif l_st_previous_next[seg_spk]['previous'] and seg_spo & l_st_previous_next[seg_spk]['previous']:
                        spo_previous_st+=1
                    elif l_st_previous_next[seg_spk]['next'] and seg_spo & l_st_previous_next[seg_spk]['next']:
                        spo_next_st+=1

                fout_spkseg.write(spk.split('#')[0]+' '+str(seg_spk.start)+' '+str(seg_spk.end)+' '+spk.split('#')[1])
                fout_spkseg.write(' '+str(spo_previous_st)+' '+str(spo_current_st)+' '+str(spo_next_st))
                fout_spkseg.write(' '+str(spo_previous_st_show)+' '+str(spo_current_st_show)+' '+str(spo_next_st_show)+' '+str(spo_other_st_show))
                fout_spkseg.write('\n')                

