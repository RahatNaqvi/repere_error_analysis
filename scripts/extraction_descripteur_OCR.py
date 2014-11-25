from pyannote.parser import MagicParser
import numpy

if __name__ == '__main__':

    parser_spk = MagicParser().read('../reference/test2.repere')
    parser_ocr = MagicParser().read('../reference/test2.OCR.repere')
    parser_uem = MagicParser().read('../reference/test2.uem')

    fout_spkshow = open('../spkshow/data/descripteur_prediction/test2.spkshow.OCR', 'w')
    fout_spkseg = open('../spkseg/data/descripteur_prediction/test2.spkseg.OCR', 'w')

    for show in parser_ocr.uris:
        ocr = parser_ocr(uri=show, modality="written")
        spk = parser_spk(uri=show, modality="speaker")
        uem = parser_uem(uri=show)

        list_spk = {}

        for segment, track, label in spk.itertracks(label=True):
            if type(label).__name__ != 'Unknown' and 'BFMTV_' not in label and 'LCP_' not in label :
                list_spk.setdefault(show+'#'+label, {'speech':[], 'ocr':[]})
                list_spk[show+'#'+label]['speech'].append(segment)

        for segment, track, label in ocr.itertracks(label=True):
            if show+'#'+label in list_spk:
                list_spk[show+'#'+label]['ocr'].append(segment)

        for spk in sorted(list_spk):
            #spkshow
            l_dur_OCR_uem = []
            l_dur_OCR_outuem = []
            l_dur_OCR_cooc_spk_in_uem = []
            for seg_OCR in list_spk[spk]['ocr']:

                dur_tot_OCR_in_seg_uem = 0.0
                for seg_uem in uem:
                    dur_tot_OCR_in_seg_uem+=(seg_OCR & seg_uem).duration

                if dur_tot_OCR_in_seg_uem > 0.0:
                    l_dur_OCR_uem.append(dur_tot_OCR_in_seg_uem)
                if seg_OCR.duration - dur_tot_OCR_in_seg_uem > 0.0: 
                    l_dur_OCR_outuem.append(seg_OCR.duration - dur_tot_OCR_in_seg_uem)

                for seg_spk in list_spk[spk]['speech']:
                    if seg_OCR & seg_spk:
                        l_dur_OCR_cooc_spk_in_uem.append((seg_OCR & seg_spk).duration)

            fout_spkshow.write(spk)
            if len(l_dur_OCR_uem) > 0:
                fout_spkshow.write(' '+str(numpy.sum(l_dur_OCR_uem))+" "+str(numpy.mean(l_dur_OCR_uem))+' '+str(len(l_dur_OCR_uem)))
            else:
                fout_spkshow.write(' 0.0 0.0 0')

            if len(l_dur_OCR_outuem) > 0:
                fout_spkshow.write(' '+str(numpy.sum(l_dur_OCR_outuem))+" "+str(numpy.mean(l_dur_OCR_outuem))+' '+str(len(l_dur_OCR_outuem)))
            else:
                fout_spkshow.write(' 0.0 0.0 0')

            if len(l_dur_OCR_cooc_spk_in_uem) > 0:
                fout_spkshow.write(' '+str(numpy.sum(l_dur_OCR_cooc_spk_in_uem))+" "+str(numpy.mean(l_dur_OCR_cooc_spk_in_uem))+' '+str(len(l_dur_OCR_cooc_spk_in_uem)))
            else:
                fout_spkshow.write(' 0.0 0.0 0')
            fout_spkshow.write('\n')

            #spkseg

            for seg_spk in list_spk[spk]['speech']:

                l_dur_OCR_seg = []
                for seg_OCR in list_spk[spk]['ocr']:
                    if seg_spk & seg_OCR:
                        l_dur_OCR_seg.append((seg_OCR & seg_uem).duration)

                fout_spkseg.write(spk+' '+str(seg_spk.start)+' '+str(seg_spk.end))

                if len(l_dur_OCR_seg) > 0:
                    fout_spkseg.write(' '+str(numpy.sum(l_dur_OCR_seg))+" "+str(numpy.mean(l_dur_OCR_seg))+' '+str(len(l_dur_OCR_seg)))
                else:
                    fout_spkseg.write(' 0.0 0.0 0')

                #idem spkshow
                if len(l_dur_OCR_uem) > 0:
                    fout_spkseg.write(' '+str(numpy.sum(l_dur_OCR_uem))+" "+str(numpy.mean(l_dur_OCR_uem))+' '+str(len(l_dur_OCR_uem)))
                else:
                    fout_spkseg.write(' 0.0 0.0 0')

                if len(l_dur_OCR_outuem) > 0:
                    fout_spkseg.write(' '+str(numpy.sum(l_dur_OCR_outuem))+" "+str(numpy.mean(l_dur_OCR_outuem))+' '+str(len(l_dur_OCR_outuem)))
                else:
                    fout_spkseg.write(' 0.0 0.0 0')

                if len(l_dur_OCR_cooc_spk_in_uem) > 0:
                    fout_spkseg.write(' '+str(numpy.sum(l_dur_OCR_cooc_spk_in_uem))+" "+str(numpy.mean(l_dur_OCR_cooc_spk_in_uem))+' '+str(len(l_dur_OCR_cooc_spk_in_uem)))
                else:
                    fout_spkseg.write(' 0.0 0.0 0')
                fout_spkseg.write('\n')



