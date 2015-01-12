from sklearn import tree
import numpy as np
import sys

if len(sys.argv)>1:
    minleaf=int(sys.argv[1])
else:
    minleaf=4

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
    class_score = {}
    for line in open(l_spkshow_file):                       # only for spkshow in l_spkshow_file
        desc[line[:-1]] = []
        real_score[line[:-1]] = []
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
            class_score[l[0]]=float(l[score_field-1])
            if float(l[score_field-1])==0:
                real_score[l[0]] = 0 #"pasreconnu" #0
            else:
                real_score[l[0]] = 1 #"reconnu" #1

        
    for spkshow_test in sorted(desc):
        if 1: #if desc[spkshow_test][0]>0:
            # for each spkshow, train a classifier
            X = []                                              # list of descriptors
            Y = []                                              # list of scores
            for spkshow_train in sorted(desc):
                if spkshow_test != spkshow_train: # leave-one-out
                    if desc[spkshow_train][0]>0:
                        X.append(desc[spkshow_train])
                        Y.append(real_score[spkshow_train])

            clas =  tree.DecisionTreeClassifier(min_samples_leaf=minleaf)                # define the classifier
            clas.fit(X, Y)                                      # train the classifier
            predicted_score[spkshow_test] = clas.predict(desc[spkshow_test])[0] # compute the predicted score
            f_imp.append(clas.feature_importances_)             # compute the features importance for this spkshow

    print 'spkshow real_score, predicted_score'             # print predicted score
    cumdiff=0
    cumerr=0
    nb=0
    nb0=0
    nb1=0
    cum0=0
    cum1=0
    cumerr01=0
    cumerr10=0
    for spk in sorted(real_score):
        if 1: #if desc[spk][0]>0:
            diff=abs(class_score[spk]-predicted_score[spk])
            err=abs(real_score[spk]-predicted_score[spk])
            print spk, class_score[spk],real_score[spk], predicted_score[spk], diff,err
            cumdiff += diff
            cumerr += err
            if real_score[spk]==0:
                cumerr01 +=err
                nb0 +=1
            else:
                cumerr10 +=err
                nb1 +=1

            if predicted_score[spk]==0:
                cum0 +=1
            else:
                cum1 +=1
                
            nb += 1

    # precision/rappel de la detection des 0
    corr0=nb0-cumerr01
    prec0=float(corr0)/cum0
    rec0=float(corr0)/nb0
    fm0=2*prec0*rec0/(prec0+rec0)

    corr1=nb1-cumerr10
    prec1=float(corr1)/cum1
    rec1=float(corr1)/nb1
    fm1=2*prec1*rec1/(prec1+rec1)

    print "detection 0: prec0=",prec0,"rec0=",rec0,"fm0=",fm0
    print "detection 1: prec1=",prec1,"rec1=",rec1,"fm1=",fm1
    

    cumdiff=float(cumdiff)/nb
    cumerr=float(cumerr)/nb
    print 'avgdiff=',cumdiff,'avgerr=',cumerr


    print 'feature_importances_'                            # compute the average features importance by descriptor
    for d, s in zip(l_desc, np.array(f_imp).mean(axis=0)):
        print d, round(s*100, 1)
