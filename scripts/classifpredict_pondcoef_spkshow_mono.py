from sklearn import tree
import numpy as np
import sys

if len(sys.argv)>2:
    minleafclassif=int(sys.argv[1])
    minleafpredict=int(sys.argv[2])
else:
    minleafclassif=4
    minleafpredict=1

if __name__ == '__main__':
    # field number start at 1
    desc_files = {'../spkshow/data/descripteur_prediction/test2.spkshow.seg':[2, 3, 4, 5, 6, 7, 8, 9],
                  '../spkshow/data/descripteur_prediction/test2.spkshow.maxseg': [2],
                  '../spkshow/data/descripteur_prediction/test2.spkshow.segadj': [5,6],
                  '../SPK_model/test2.spkshow.max.acoustic.DC':[2, 3, 4, 5, 6, 7],
#                  '../spkshow/data/descripteur_prediction/test2.spkshow.pitchSegRef.1.0.v2':[2, 3],
                 }

    score_file = '../spkshow/PERCOOL_QCOMPERE_SODA_mono.durevalf.spkshow'
    score_field = 7
    l_spkshow_file = '../reference/list_spkshow_mono'

    desc = {}                                               # dictionary of the spkshow/descriptors
    real_score = {}                                         # dictionary of the spkshow/real scores
    predicted_score = {}                                    # dictionary of the spkshow/predicted scores
    real_class = {}
    for line in open(l_spkshow_file):                       # only for spkshow in l_spkshow_file
        desc[line[:-1]] = []
        real_score[line[:-1]] = []
        real_class[line[:-1]] = []
        predicted_score[line[:-1]] = []

    f_imp = []                                              # list of the features importance
    l_desc = []                                             # list of the descriptor names (filename #field) in the same order than in desc
    for f in sorted(desc_files):     
        for i in desc_files[f]:
            l_desc.append(f.split('/')[-1]+' field'+str(i))

    for f in sorted(desc_files):                                    # file descriptor dictionary
        for line in open(f):
            l = line[:-1].split(' ')   
            if l[0] in desc:         
                for i in sorted(desc_files[f]):
                    desc[l[0]].append(float(l[i-1]))

                    # desc[spkshow][0]: duree totale de train pour le spkshow
    
    for line in open(score_file):                           # file real_score dictionary
        l = line[:-1].split(' ')
        if l[0] in real_score:
            real_score[l[0]]=float(l[score_field-1])
            if float(l[score_field-1])==0:
                real_class[l[0]] = 0 #"pasreconnu" #0
            else:
                real_class[l[0]] = 1 #"reconnu" #1

    pondclassif=[1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1]  # optimum trouve par optidiscardcoef_classif_spkshow_mono.py
    pondpredict=[0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1] # optimum trouve par optidiscardcoef_classifpredict_spkshow_mono.py

    for spkshow_test in sorted(desc):
        if 1: #if desc[spkshow_test][0]>0:
            # for each spkshow, train a classifier
            desctestclassif=[]
            for j in range(len(pondclassif)):
                if (pondclassif[j]>0):
                    desctestclassif.append(desc[spkshow_test][j])
            desctestpredict=[]
            for j in range(len(pondpredict)):
                if (pondpredict[j]>0):
                    desctestpredict.append(desc[spkshow_test][j])
                    
            Xclassif = []                                              # list of descriptors
            Y = []                                              # list of class label
            for spkshow_train in sorted(desc):
                if spkshow_test != spkshow_train: # leave-one-out
                    usedescclassif=[]
                    for j in range(len(pondclassif)):
                        if (pondclassif[j]>0):
                            usedescclassif.append(desc[spkshow_train][j])
                    Xclassif.append(usedescclassif)
                    #X.append(desc[spkshow_train])
                    Y.append(real_class[spkshow_train])

            clas =  tree.DecisionTreeClassifier(min_samples_leaf=minleafclassif)                # define the classifier
            clas.fit(Xclassif, Y)                                      # train the classifier
            predicted_score[spkshow_test] = clas.predict(desctestclassif)[0] # compute the predicted score 
            
            if predicted_score[spkshow_test]==1: # c'est un spkshow predit non nul, on essaie de predire sa fmax
                # on apprend en loo une regression sur les spkshow>0
                Xpredict = []                                              # list of descriptors
                Y = []                                              # list of scores
                for spkshow_train in sorted(desc):
                    if spkshow_test != spkshow_train: # leave-one-out
                        if real_score[spkshow_train]>0:
                            usedescpredict=[]
                            for j in range(len(pondpredict)):
                                if (pondpredict[j]>0):
                                    usedescpredict.append(desc[spkshow_train][j])
                            Xpredict.append(usedescpredict)
                            #X.append(desc[spkshow_train])
                            Y.append(real_score[spkshow_train])
                        
                pred = tree.DecisionTreeRegressor(min_samples_leaf=minleafpredict)
                pred.fit(Xpredict,Y)
                predicted_score[spkshow_test]=pred.predict(desctestpredict)[0]
                f_imp.append(pred.feature_importances_)             # compute the f
    print 'spkshow real_score, predicted_score'             # print predicted score
    cumdiff=0
    nb=0
    for spk in sorted(real_score):
        if 1: #if desc[spk][0]>0:
            diff=abs(real_score[spk]-predicted_score[spk])
            print spk, real_score[spk], predicted_score[spk], diff
            cumdiff += diff
            nb += 1

    

    cumdiff=float(cumdiff)/nb
    print 'avgdiff=',cumdiff

    l_desc_extract=[]
    for j in range(len(pondpredict)):
        if pondpredict[j]>0:
            l_desc_extract.append(l_desc[j])


    print 'feature_importances_'                            # compute the average features importance by descriptor
    for d, s in zip(l_desc_extract, np.array(f_imp).mean(axis=0)):
        print d, round(s*100, 1)
