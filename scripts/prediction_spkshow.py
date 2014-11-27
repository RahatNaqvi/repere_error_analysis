from sklearn.linear_model import LogisticRegression
import numpy


def convert(value, type_):
    import importlib
    try:
        # Check if it's a builtin type
        module = importlib.import_module('__builtin__')
        cls = getattr(module, type_)
    except AttributeError:
        # if not, separate module and class
        module, type_ = type_.rsplit(".", 1)
        module = importlib.import_module(module)
        cls = getattr(module, type_)
    return cls(value)

if __name__ == '__main__':
    desc_files = {'../spkshow/data/descripteur_prediction/test2.spkshow.OCR':['float', 'float', 'int', 'float', 'float', 'int', 'float', 'float', 'int'],    
                  '../spkshow/data/descripteur_prediction/test2.spkshow.seg':['float', 'float', 'int', 'float', 'int'],             
                  '../spkshow/data/descripteur_prediction/test2.spkshow.spoken':['int', 'int', 'int', 'int'], 
                  #'../spkshow/test2.spkshow.role':['str'],
                  '../SPK_model/test2.spkshow.max.acoustic':['float', 'int','float', 'int','float', 'int'],
                 }

    score_file = '../spkshow/PERCOOL_QCOMPERE_SODA_sup.durevalf.spkshow'
    l_spkshow_file = '../reference/list_spkshow'

    desc = {}
    score = {}
    for line in open(l_spkshow_file):
        desc[line[:-1]] = []
        score[line[:-1]] = []

    for f in desc_files:
        for line in open(f):
            l = line[:-1].split(' ')   
            if l[0] in desc:         
                for i in range(len(desc_files[f])):
                    d = convert(l[i+1], desc_files[f][i])
                    desc[l[0]].append(d)
    
    for line in open(score_file):
        l = line[:-1].split(' ')
        if l[0] in score:
            score[l[0]] = float(l[4])
           
    ecarts = []  
    for spk_test in sorted(desc):
        X = []
        Y = []
        for spk_train in sorted(desc):
            if spk_test != spk_train:
                X.append(desc[spk_train])
                Y.append(score[spk_train])

        clas =  LogisticRegression()
        clas.fit(X, Y)
        predic_score = clas.predict(desc[spk_test])[0]
        #print spk_test, predic_score, score[spk_test], abs(predic_score-score[spk_test])
        ecarts.append(abs(predic_score-score[spk_test]))
    print numpy.mean(ecarts)


