# -*- coding: utf-8 -*-
import numpy as np
import pylab as plt

if __name__ == '__main__':
    l_spkshow_file = '../reference/list_spkshow'
    l_spkseg_file = '../reference/list_spkseg'
    score_file_spkshow = {'f':'../spkshow/PERCOOL_QCOMPERE_SODA_sup.durevalf.spkshow', 'field':2}
    score_file_spkseg = {'f':'../spkseg/evalSegHB/PERCOOL_sup.repere.evalsegHB', 'field':4}

    score_spkshow = {}
    lower_ecart = [1.0, 0.0]
    for line in open(l_spkshow_file):
        score_spkshow[line[:-1]] = []

    for line in open(score_file_spkshow['f']):
        l = line[:-1].split(' ')
        if l[0] in score_spkshow:
            score_spkshow[l[0]] = float(l[score_file_spkshow['field']])

    val = []
    for predic_score in np.arange(0,1.01,0.05):
        ecart = []
        for spk_test in sorted(score_spkshow):
            ecart.append(abs(predic_score-score_spkshow[spk_test]))
        val.append(round(np.mean(ecart),3))
        if round(np.mean(ecart),3) < lower_ecart[0]:
            lower_ecart = [round(np.mean(ecart),3), round(predic_score, 2)]
    print 'spkshow lower ecart', lower_ecart
    fig1 = plt.figure()
    fig1.suptitle('ecart/prediction baseline spkshow', fontsize=14, fontweight='bold')
    plt.ylabel('ecart')
    plt.xlabel('prediction')

    plt.plot(np.arange(0,1.01,0.05), val)
    plt.ylim([0,1])
    plt.figtext(.01, .01, "plus petit ecart : "+str(lower_ecart[0])+" pour prediction="+str(lower_ecart[1]))
    fig1.savefig('spkshow_base_line')
    plt.show()


    score_spkseg = {}
    lower_ecart = [1.0, 0.0]    
    for line in open(l_spkseg_file):
        l = line[:-1].split(' ')
        score_spkseg.setdefault(l[0]+'#'+l[3], {})
        score_spkseg[l[0]+'#'+l[3]][l[1]+' '+l[2]] = [] 

    for line in open(score_file_spkseg['f']):
        l = line[:-1].split(' ')
        spk = l[0]+'#'+l[3]
        seg = str(float(l[1]))+' '+str(float(l[2]))
        if spk in score_spkseg:
            corr = float(l[5])
            conf = float(l[6])
            miss = float(l[7])
            fa  = float(l[8])
            nb_hyp = corr + conf + fa
            nb_ref = corr + conf + miss
            R=0.0
            P=0.0
            if nb_ref>0:
                R = corr/nb_ref
            if nb_hyp>0:
                P = corr/nb_hyp
            F = 0.0
            if P+R > 0:
                F = (2*R*P)/(R+P)
            score_spkseg[spk][seg] = F
            #score_spkseg[spk][seg] = float(l[score_file_spkseg['field']])

    val = []
    for predic_score in np.arange(0,1.01,0.05):
        ecart = []  
        for spk_test in sorted(score_spkseg):
            for seg in score_spkseg[spk_test]:
                ecart.append(abs(predic_score-score_spkseg[spk_test][seg]))
        val.append(round(np.mean(ecart),3))
        if round(np.mean(ecart),3) < lower_ecart[0]:
            lower_ecart = [round(np.mean(ecart),3), round(predic_score, 2)]
    print 'spkseg lower ecart', lower_ecart

    fig1 = plt.figure()
    fig1.suptitle('ecart/prediction baseline spkseg', fontsize=14, fontweight='bold')
    plt.ylabel('ecart')
    plt.xlabel('prediction')

    plt.plot(np.arange(0,1.01,0.05), val)
    plt.ylim([0,1])
    plt.figtext(.01, .01, "plus petit ecart : "+str(lower_ecart[0])+" pour prediction="+str(lower_ecart[1]))
    fig1.savefig('spkseg_base_line')
    plt.show()





