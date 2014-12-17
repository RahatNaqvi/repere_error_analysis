from sklearn import tree
import numpy as np

if __name__ == '__main__':

    desc_files = {'../spkshow/data/descripteur_prediction/test2.spkshow.seg':[2, 3, 4, 5, 6, 7, 8, 9],             
                  '../SPK_model/test2.spkshow.max.acoustic':[2, 3, 4, 5, 6, 7],
                  '../spkshow/data/descripteur_prediction/test2.spkshow.pitchSegRef.1.0.v2':[2, 3],
                 }

    score_file = '../spkshow/PERCOOL_QCOMPERE_SODA_mono.durevalf.spkshow'
    score_field = 6
    l_spkshow_file = '../reference/list_spkshow'

    desc = {}                                               # dictionary of the spkshow/descriptors
    real_score = {}                                         # dictionary of the spkshow/real scores
    predicted_score = {}                                    # dictionary of the spkshow/predicted scores
    for line in open(l_spkshow_file):                       # only for spkshow in l_spkshow_file
        desc[line[:-1]] = []
        real_score[line[:-1]] = []
        predicted_score[line[:-1]] = []

    f_imp = []                                              # list of the features importance
    l_desc = []                                             # list of the descriptor names (filename #field) in the same order than in desc
    for f in desc_files:     
        for i in desc_files[f]:
            l_desc.append(f.split('/')[-1]+' field'+str(i))

    for f in desc_files:                                    # file descriptor dictionary
        for line in open(f):
            l = line[:-1].split(' ')   
            if l[0] in desc:         
                for i in desc_files[f]:
                    desc[l[0]].append(float(l[i-1]))
    
    for line in open(score_file):                           # file real_score dictionary
        l = line[:-1].split(' ')
        if l[0] in real_score:
            real_score[l[0]] = float(l[score_field])
   
    for spkshow_test in sorted(desc):                       # for each spkshow, train a classifier
        X = []                                              # list of descriptors
        Y = []                                              # list of scores
        for spkshow_train in sorted(desc):
            if spkshow_test != spkshow_train:               # leave one out
                X.append(desc[spkshow_train])
                Y.append(real_score[spkshow_train])

        clas =  tree.DecisionTreeRegressor()                # define the classifier
        clas.fit(X, Y)                                      # train the classifier
        predicted_score[spkshow_test] = clas.predict(desc[spkshow_test])[0] # compute the predicted score
        f_imp.append(clas.feature_importances_)             # compute the features importance for this spkshow

    print 'spkshow real_score, predicted_score'             # print predicted score
    for spk in sorted(real_score):
        print spk, real_score[spk], predicted_score[spk]
    print 

    print 'feature_importances_'                            # compute the average features importance by descriptor
    for d, s in zip(l_desc, np.array(f_imp).mean(axis=0)):
        print d, round(s*100, 1)
