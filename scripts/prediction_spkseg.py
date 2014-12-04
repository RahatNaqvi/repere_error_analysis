from sklearn.linear_model import LogisticRegression
from sklearn import tree
from random import randint
import numpy
from pylab import *

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
    desc_files_spk = {'../SPK_model/test2.spkshow.3sites.acoustic':['float', 'int','float', 'int','float', 'int'],
                     }
    score_file = {'f':'../spkseg/evalSegHB/PERCOOL_sup.repere.evalsegHB', 'field':4}
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

    for line in open(score_file['f']):
        l = line[:-1].split(' ')
        spk = l[0]+'#'+l[3]
        seg = str(float(l[1]))+' '+str(float(l[2]))
        if spk in score:
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
            score[spk][seg] = F
            #score[spk][seg] = float(l[score_file['field']])
           
    dic_clas = {}
    x=[]
    y=[]

    ecart = []
    for spk_test in sorted(desc):
        X = []
        Y = []
        for spk_train in sorted(desc):
            if spk_test != spk_train:
                for seg in desc[spk_train]:
                    X.append(desc[spk_train][seg])
                    Y.append(score[spk_train][seg])

        clas =  tree.DecisionTreeRegressor()
        clas.fit(X, Y)
        for seg in desc[spk_test]:        
            predic_score = clas.predict(desc[spk_test][seg])[0]
            x.append(predic_score)
            y.append(score[spk_test][seg])
            ecart.append(score[spk_test][seg]-predic_score)

    print numpy.mean(ecart)    
    fig1 = plt.figure()
    fig1.suptitle('histogramme (scores mesures - predictions)', fontsize=14, fontweight='bold')
    plt.xlabel('valeur des ecarts')
    plt.ylabel("# d'ecarts")

    bins = np.arange(-1.0,1.0,0.05)
    plt.hist(ecart, bins, normed=True)
    fig1.savefig('spkseg_histo_ecart')
    plt.show()


    fig1 = plt.figure()
    fig1.suptitle('predictions / scores mesures', fontsize=14, fontweight='bold')
    plt.ylabel('prediction')
    plt.xlabel("scores mesures")

    bins = np.arange(0,1.01,0.05)
    plt.plot(x, y, 'ro') 
    plt.axis([0,1,0,1])
    plt.grid()
    fig1.savefig('spkseg_nuage')
    plt.show() 

