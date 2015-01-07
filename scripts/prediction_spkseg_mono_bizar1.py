from sklearn import tree
import numpy as np

if __name__ == '__main__':
    # field number start at 1
    l_desc_files_spkseg = {'../spkSeg/data/descripteur_prediction/test2.spkseg.seg':[5, 6, 7, 8, 9, 10],
#                           '../spkSeg/data/descripteur_prediction/test2.spkseg.pitchSegRef.1.0.v2.goodspkseg':[5, 6], 
                           '../spkSeg/data/descripteur_prediction/test2.spkseg.pitchSegRef.1.0.v2':[5, 6], 
                          }
    l_desc_files_spkshow = {'../SPK_model/test2.spkshow.max.acoustic.DC':[2, 3, 4, 5, 6, 7],
                           }
    score_file_spkseg = '../spkSeg/evalSegSM/PERCOOL_QCOMPERE_SODA_mono.SM1.0.evalseg.spkshowmax.idseg'
    field_score_file_spkseg = 7
    field_score_file_spkshow = 8

    f_imp = []                                              # list of the features importance
    l_desc = []                                             # list of the descriptor names (filename #field) in the same order than in desc
    for f in l_desc_files_spkseg:     
        for i in l_desc_files_spkseg[f]:
            l_desc.append(f.split('/')[-1]+' field'+str(i))
    for f in l_desc_files_spkshow:     
        for i in l_desc_files_spkshow[f]:
            l_desc.append(f.split('/')[-1]+' field'+str(i))
    
    desc = {}                                               # dictionary of the spkshow/descriptors
    real_score = {}                                         # dictionary of the spkshow/real scores
    predicted_score = {}                                    # dictionary of the spkshow/predicted scores
    for line in open(score_file_spkseg):                    # file real_score dictionary
        l = line[:-1].split(' ')
        spk = l[0].split('#')[0]+'#'+l[0].split('#')[3]
        seg = str(float(l[0].split('#')[1]))+' '+str(float(l[0].split('#')[2]))
        if float(l[field_score_file_spkshow-1]) != 0:         # only for spk recognizable
            real_score.setdefault(spk, {})
            real_score[spk][seg] = float(l[field_score_file_spkseg-1])/100
            predicted_score.setdefault(spk, {})
            predicted_score[spk][seg] = {}

    for f in l_desc_files_spkseg:                           # file descriptor dictionary at spkseg level
        for line in open(f):
            l = line[:-1].split(' ')
            spk = l[0]+'#'+l[3]
            seg = str(float(l[1]))+' '+str(float(l[2]))
            if spk in real_score:     
                if seg in real_score[spk]:   
                    for i in l_desc_files_spkseg[f]:
                        desc.setdefault(spk, {})
                        desc[spk].setdefault(seg, []).append(float(l[i-1]))
    for f in l_desc_files_spkshow:                          # file descriptor dictionary at spkshow level
        for line in open(f):
            l = line[:-1].split(' ')
            spk = l[0]
            if spk in real_score:   
                for seg in real_score[spk]:                
                    for i in l_desc_files_spkshow[f]:
                        desc.setdefault(spk, {})
                        desc[spk].setdefault(seg, []).append(float(l[i-1]))

    for spk in sorted(desc):                                # for each spkshow, train a classifier
        X = []                                              # list of descriptors
        Y = []                                              # list of scores
        for spk_train in sorted(desc):
            if spk != spk_train:                            # leave one out
                for seg in desc[spk_train]:                 # for each seg in spkshow
                    X.append(desc[spk_train][seg])
                    Y.append(real_score[spk_train][seg])
        clas =  tree.DecisionTreeRegressor()                # define the classifier
        clas.fit(X, Y)                                      # train the classifier
        for seg in desc[spk]:      
            predicted_score[spk][seg] = clas.predict(desc[spk][seg])[0] # compute the predicted score
        f_imp.append(clas.feature_importances_)             # compute the features importance for this spkshow

    print 'spkshow start end real_score, predicted_score'   # print predicted score
    #for spk in sorted(real_score):
        #for seg in sorted(real_score[spk]):
            #print spk, seg, real_score[spk][seg], predicted_score[spk][seg]

    print 'feature_importances_'                            # compute the average features importance by descriptor
    for d, s in zip(l_desc, np.array(f_imp).mean(axis=0)):
        print d, round(s*100, 1)

