from sklearn.linear_model import LogisticRegression
from sklearn import tree
import numpy as np
import pylab as plt
import random

if __name__ == '__main__':
    desc_files = {'../spkshow/data/descripteur_prediction/test2.spkshow.OCR':[1, 2, 3, 4, 5, 6, 7, 8, 9],    
                  '../spkshow/data/descripteur_prediction/test2.spkshow.seg':[1, 2, 3, 4, 5],             
                  '../spkshow/data/descripteur_prediction/test2.spkshow.spoken':[1, 2, 3, 4], 
                  '../SPK_model/test2.spkshow.max.acoustic':[1, 2, 3, 4, 5, 6],
                 }

    score_file = {'f':'../spkshow/PERCOOL_QCOMPERE_SODA_mono.durevalf.spkshow', 'field':6}
    l_spkshow_file = '../reference/list_spkshow'

    desc = {}
    score = {}
    x = []
    y = []
    for line in open(l_spkshow_file):
        desc[line[:-1]] = []
        score[line[:-1]] = []

    for f in desc_files:
        for line in open(f):
            l = line[:-1].split(' ')   
            if l[0] in desc:         
                for i in desc_files[f]:
                    desc[l[0]].append(float(l[i]))
    
    for line in open(score_file['f']):
        l = line[:-1].split(' ')
        if l[0] in score:
            score[l[0]] = float(l[score_file['field']])


    ecart = []
    for spk_test in sorted(desc):
        X = []
        Y = []
        for spk_train in sorted(desc):
            if spk_test != spk_train:
                X.append(desc[spk_train])
                Y.append(score[spk_train])

        clas =  tree.DecisionTreeRegressor()
        clas.fit(X, Y)
        predic_score = clas.predict(desc[spk_test])[0]
        x.append(predic_score)
        y.append(score[spk_test])
        ecart.append(score[spk_test]-predic_score)

        #print spk_test, predic_score, score[spk_test], abs(predic_score-score[spk_test])

    print np.mean(ecart)
    fig1 = plt.figure()
    fig1.suptitle('histogramme (scores mesures - predictions)', fontsize=14, fontweight='bold')
    plt.ylabel('valeur des ecarts')
    plt.xlabel("# d'ecarts")

    bins = np.arange(-1.0,1.0,0.05)
    plt.hist(ecart, bins, normed=True)
    fig1.savefig('spkshow_histo_ecart')
    plt.show()


    fig1 = plt.figure()
    fig1.suptitle('predictions / scores mesures', fontsize=14, fontweight='bold')
    plt.ylabel('prediction')
    plt.xlabel("scores mesures")

    bins = np.arange(0,1.01,0.05)
    plt.plot(x, y, 'ro') 
    plt.axis([0,1,0,1])
    plt.grid()
    fig1.savefig('spkshow_nuage')
    plt.show() 
