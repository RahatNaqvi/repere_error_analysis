import numpy as np

if __name__ == '__main__':
    l_spkshow_file = '../reference/list_spkshow'
    l_spkseg_file = '../reference/list_spkseg'
    score_file_spkshow = '../spkshow/PERCOOL_QCOMPERE_SODA_sup.durevalf.spkshow'
    score_file_spkseg = '../spkseg/evalSegHB/PERCOOL_sup.repere.evalsegHB'

    print 'spkshow'
    score_spkshow = {}
    for line in open(l_spkshow_file):
        score_spkshow[line[:-1]] = []

    for line in open(score_file_spkshow):
        l = line[:-1].split(' ')
        if l[0] in score_spkshow:
            score_spkshow[l[0]] = float(l[4])

    for predic_score in np.arange(0,1.01,0.05):
        print round(predic_score,2), '\t',
    print
    for predic_score in np.arange(0,1.01,0.05):
        ecarts = []  
        for spk_test in sorted(score_spkshow):
            ecarts.append(abs(predic_score-score_spkshow[spk_test]))
        print round(np.mean(ecarts),3), '\t',
    print

    print 'spkseg'
    score_spkseg = {}
    for line in open(l_spkseg_file):
        l = line[:-1].split(' ')
        score_spkseg.setdefault(l[0]+'#'+l[3], {})
        score_spkseg[l[0]+'#'+l[3]][l[1]+' '+l[2]] = [] 

    for line in open(score_file_spkseg):
        l = line[:-1].split(' ')
        spk = l[0]+'#'+l[3]
        seg = str(float(l[1]))+' '+str(float(l[2]))
        if spk in score_spkseg:
            score_spkseg[spk][seg] = float(l[4])

    for predic_score in np.arange(0,1.01,0.05):
        print round(predic_score,2), '\t',
    print
    for predic_score in np.arange(0,1.01,0.05):
        ecarts = []  
        for spk_test in sorted(score_spkseg):
            for seg in score_spkseg[spk_test]:
                ecarts.append(abs(predic_score-score_spkseg[spk_test][seg]))
        print round(np.mean(ecarts),3), '\t',
    print





