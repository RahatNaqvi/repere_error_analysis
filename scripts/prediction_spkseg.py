from sklearn.linear_model import LogisticRegression
from random import randint
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
    desc_files_seg = {'../spkseg/data/descripteur_prediction/test2.spkseg.OCR':['float', 'float', 'int', 'float', 'float', 'int', 'float', 'float', 'int', 'float', 'float', 'int'],    
                      '../spkseg/data/descripteur_prediction/test2.spkseg.seg':['float', 'float', 'int', 'float', 'float', 'int'],             
                      '../spkseg/data/descripteur_prediction/test2.spkseg.spoken':['int', 'int', 'int', 'int', 'int', 'int'], 
                      #'../spkseg/test2.spkseg.role':['str'],
                     }

    desc_files_spk = {'../SPK_model/test2.spkshow.max.acoustic':['float', 'int','float', 'int','float', 'int'],
                     }

    score_file = '../spkseg/evalSeg2/PERCOOL_sup.evalseg'
    l_spkseg_file = '../reference/list_spkseg'


    desc = {}
    score = {}
    for line in open(l_spkseg_file):
        l = line[:-1].split(' ')
        desc.setdefault(l[0]+'#'+l[3], {})
        score.setdefault(l[0]+'#'+l[3], {})
        desc[l[0]+'#'+l[3]][l[1]+' '+l[2]] = []
        score[l[0]+'#'+l[3]][l[1]+' '+l[2]] = []

    for f in desc_files_seg:
        for line in open(f):
            l = line[:-1].split(' ')
            spk = l[0]+'#'+l[3]
            seg = l[1]+' '+l[2]
            if spk in desc:         
                for i in range(len(desc_files_seg[f])):
                    d = convert(l[i+4], desc_files_seg[f][i])
                    desc[spk][seg].append(d)
    
    for f in desc_files_spk:
        for line in open(f):
            l = line[:-1].split(' ')
            spk = l[0]
            if spk in desc:
                for seg in desc[spk]:                
                    for i in range(len(desc_files_spk[f])):
                        d = convert(l[i+1], desc_files_spk[f][i])
                        desc[spk][seg].append(d)

    for line in open(score_file):
        l = line[:-1].split(' ')
        spk = l[0]+'#'+l[3]
        seg = str(float(l[1]))+' '+str(float(l[2]))
        if spk in score:
            score[spk][seg] = float(l[4])
           
    ecarts = [] 
    nb_fold = 5
    dic_fold = {'spk':{}, 'fold':{}}
    for spk in desc: 
        fold = randint(0, nb_fold-1)
        dic_fold['spk'][spk] = fold
        dic_fold['fold'].setdefault(fold, []).append(spk)

    dic_clas = {}
    for i in range(nb_fold):
        X = []
        Y = []        
        for spk_train in sorted(desc):
            if dic_fold['spk'][spk_train] not in dic_fold['fold'][i]:
                for seg in desc[spk_train]:
                    X.append(desc[spk_train][seg])
                    Y.append(score[spk_train][seg])
        clas = LogisticRegression()
        clas.fit(X, Y)
        dic_clas[i] = clas

    for spk_test in sorted(desc):
        for seg in desc[spk_test]:
            predic_score = dic_clas[dic_fold['spk'][spk_test]].predict(desc[spk_test][seg])[0]
            #print spk_test, seg, predic_score, score[spk_test][seg], abs(predic_score-score[spk_test][seg])
            ecarts.append(abs(predic_score-score[spk_test][seg]))
    print numpy.mean(ecarts)

