from sklearn import tree
import numpy as np
import sys

if len(sys.argv)>1:
    minleaf=int(sys.argv[1])
else:
    minleaf=12

    

if __name__ == '__main__':
    # field number start at 1
    l_desc_files_spkseg = {'../spkSeg/data/descripteur_prediction/test2.spkseg.seg':[5, 6, 7, 8, 9, 10],
                           #'../spkSeg/data/descripteur_prediction/test2.spkseg.pitchSegRef.1.0.v2.formatOK':[5, 6],
                           '../spkSeg/data/descripteur_prediction/test2.spkseg.segadj':[8,9],
                          }
    l_desc_files_spkshow = {
        '../SPK_model/test2.spkshow.max.acoustic.DC':[2, 3, 4, 5, 6, 7],
        #'../SPK_model/test2.spkshow.max.acoustic.DC':[2, 3],
#                  '../spkshow/data/descripteur_prediction/test2.spkshow.maxseg': [2],          
                           }
    score_file_spkseg = '../spkSeg/evalSegSM/PERCOOL_QCOMPERE_SODA_mono.SM1.0.evalseg.spkshowmax.idseg'
    # field_score_file_spkseg = 7 (scoremax du seg)
    field_score_file_spkseg = 9 # score du seg du system donnant scoremax spkshow
    field_score_file_spkshow = 8
    l_spkshow_file = '../reference/list_spkshow_mono_reconnu'
    


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

    for line in open(l_spkshow_file):                       # only for spkshow in l_spkshow_file
        spk=line[:-1]
        real_score.setdefault(spk, {})

    for line in open(score_file_spkseg):                    # file real_score dictionary
        l = line[:-1].split(' ')
        spk = l[0].split('#')[0]+'#'+l[0].split('#')[3]
        seg = str(float(l[0].split('#')[1]))+' '+str(float(l[0].split('#')[2]))
        # ci-dessous: condition sur les spkshow au moins une fois dans le doc
        #if float(l[field_score_file_spkshow-1]) != 0:         # only for spk recognizable
        # ci-dessous: condition sur les spkshow appartenant a une liste specifie: ici, ceux qui ont un modele acoustique
        if spk in real_score:
            real_score.setdefault(spk, {})
            if float(l[field_score_file_spkseg-1])==0:
                real_score[spk][seg]=0
            else:
                real_score[spk][seg]=1
            
                
            #real_score[spk][seg] = float(l[field_score_file_spkseg-1])/100
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
        clas =  tree.DecisionTreeClassifier(min_samples_leaf=minleaf)                # define the classifier
        clas.fit(X, Y)                                      # train the classifier
        for seg in desc[spk]:      
            predicted_score[spk][seg] = clas.predict(desc[spk][seg])[0] # compute the predicted score
        f_imp.append(clas.feature_importances_)             # compute the features importance for this spkshow

    print 'spkshow start end real_score, predicted_score'   # print predicted score
    cumdiff=0
    nb=0
    cumerr=0
    nb=0
    nb0=0
    nb1=0
    cum0=0
    cum1=0
    cumerr01=0
    cumerr10=0
    for spk in sorted(real_score):
         for seg in sorted(real_score[spk]):
            print spk, seg, real_score[spk][seg], predicted_score[spk][seg],abs(real_score[spk][seg]-predicted_score[spk][seg]) 
            cumdiff += abs(real_score[spk][seg]-predicted_score[spk][seg])
            err=abs(real_score[spk][seg]-predicted_score[spk][seg])
            cumerr += err
            if real_score[spk][seg]==0:
                cumerr01 +=err
                nb0 +=1
            else:
                cumerr10 +=err
                nb1 +=1

            if predicted_score[spk][seg]==0:
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

    print "detection 0: nb0=",nb0," prec0=",prec0,"rec0=",rec0,"fm0=",fm0
    print "detection 1: nb1=",nb1," prec1=",prec1,"rec1=",rec1,"fm1=",fm1
    

    cumdiff=float(cumdiff)/nb
    cumerr=float(cumerr)/nb
    print 'avgdiff=',cumdiff,'avgerr=',cumerr
 
    print 'feature_importances_'                            # compute the average features importance by descriptor
    for d, s in zip(l_desc, np.array(f_imp).mean(axis=0)):
        print d, round(s*100, 1)

