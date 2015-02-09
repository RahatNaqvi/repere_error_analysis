# -*- coding: utf-8 -*-

'''
Created on 14 déc. 2014

@author: meignier
'''
import re as regexp
import copy
import logging
import os
import sys
import argparse
import matplotlib.pyplot as plt
import numpy as np

try:
    from sortedcontainers import SortedDict as dict
except ImportError:
    pass

class Index(dict):
    """Implementation of perl's autovivification feature."""

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class ColNames:
    def __init__(self):
        self.names = dict
        self.defaults = list

    # def deepcopy(self):
    # ncol = ColNames()
    # ncol.defaults = copy.deepcopy(self.defaults)
    # ncol.names = copy.deepcopy(self.names)
    #     return ncol

    def index_of(self, name):
        return self.names[name]

    def exist(self, name):
        return name in self.names

    def initialize(self, names, defaults):
        self.names = names
        self.defaults = defaults

    def __getitem__(self, index):
        return self.names[index]

    def __setitem__(self, index, value):
        return self.names.__setitem__(index, value)

    def __iter__(self):
        return self.names.__iter__()

    def __len__(self):
        return self.defaults.__len__()

    def sorted(self):
        return sorted(self.names.items(), key=lambda x: x[1])

    def add(self, name, default=''):
        if name in self.names:
            raise Exception('This column exits : ')
        else:
            self[name] = len(self.defaults)
            self.defaults.append(default)

    def delete(self, name):
        if name not in self.names:
            raise Exception("This column don't exits : " + name)
        else:
            i = self[name]
            del self.defaults[i]
            del self.names[name]
            for k in self.names:
                if self.names[k] > i:
                    self.names[k] -= 1


class Row(list):
    def __init__(self, data, colNames):
        list.__init__(self)
        self.colNames = colNames
        for item in data:
            self.append(item)

    def _get_col(self, name):
        return self[self.colNames[name]]

    def _set_col(self, name, value):
        self[self.colNames[name]] = value

    def __getitem__(self, index):
        if isinstance(index, str):
            return self._get_col(index)
        else:
            return list.__getitem__(self, index)

    def __setitem__(self, index, value):
        if isinstance(index, str):
            return self._set_col(index, value)
        else:
            return list.__setitem__(self, index, value)

    def length(self):
        return self['stop'] - self['start']

    def seg_features(self, features):
        return features[self['start']:self['stop'], :]

    @classmethod
    def gap(cls, row1, row2):
        if row1['show'] != row2['show']:
            raise Exception('not the same show')
        data = copy.deepcopy(row1)
        data['start'] = data['stop']
        data['stop'] = row2['start']
        return Row(data, row1.colNames)

    @classmethod
    def intersection(cls, row1, row2):
        if len(row1) != len(row2):
            raise Exception('not the same row format ' + row1 + ' != ' + row2)
        if row1['show'] != row2['show']:
            raise Exception(
                'not the same show ' + row1['show'] + ' != ' + row2['show'])
        row = row1.copy()
        for idx in row1.colNames:
            if idx not in ['start', 'stop']:
                if row1[idx] != row2[idx]:
                    row[idx] = row1[idx] + '+' + row2[idx]
        row['start'] = max(row1['start'], row2['start'])
        row['stop'] = min(row1['stop'], row2['stop'])
        return row

    @classmethod
    def union(cls, row1, row2):
        if len(row1) != len(row2):
            raise Exception('not the same row format ' + row1 + ' != ' + row2)
        if row1['show'] != row2['show']:
            raise Exception('not the same show ' +
                            row1['show'] + ' != ' + row2['show'])
        row = row1.copy()
        for idx in row1.colNames:
            if idx not in ['start', 'stop']:
                if row1[idx] != row2[idx]:
                    row[idx] = row1[idx] + '+' + row2[idx]
        row['start'] = min(row1['start'], row2['start'])
        row['length'] = max(row1['stop'], row2['stop']) - row['start']
        return row


class Table():
    def __init__(self):
        self.colNames = ColNames()
        self.colNames.initialize({'show': 0, 'label': 1, 'labelType': 2,
                                  'start': 3, 'stop': 4},
                                 ['empty', 'empty', 'speaker', 0, 0])
        self.labelTypes = ['speaker', 'head']
        self.rows = list()

    def copy_structure(self):
        ntable = Table()
        ntable.colNames = copy.deepcopy(self.colNames)
        ntable.labelTypes = copy.deepcopy(self.labelTypes)
        return ntable

    def del_all(self, key, value):
        lst = list()
        for row in self.rows:
            if row[key] != value:
                lst.append(row)
        self.rows = lst

    def filter(self, key, ope, value):
        ntable = self.copy_structure()
        ntable.rows = list()
        ch = "row['{:s}'] {:s} {:s}".format(key, ope, value)
        logging.debug(ch)
        for row in self.rows:
            if eval(ch):
                ntable.rows.append(copy.deepcopy(row))
        return ntable

    def rename(self, col_name, lst, new_name):
        for row in self.rows:
            if row[col_name] in lst:
                row[col_name] = new_name

    def _iofi(self, index, names, row):
        col = names.pop()
        value = row[col]
        if len(names) <= 0:
            if value in index:
                index[value].append(row)
            else:
                index[value] = [row]
            return index
        else:
            self._iofi(index[value], names, row)

    def make_index(self, names):
        index = Index()
        for row in self.rows:
            self._iofi(index, names[::-1], row)
        return index

    def unique(self, name):
        d = dict()
        l = list()
        for row in self.rows:
            d[row[name]] = 0
        for v in d.keys():
            l.append(v)
        return l

    def sort(self, lst=['show', 'start'], reverse=False):
        for col in lst:
            if col not in self.colNames:
                raise Exception("This column don't exits : " + col)
            self.rows = sorted(self.rows, key=lambda x: x[self.colNames[col]],
                               reverse=reverse)

    def clear(self):
        self.rows = list()

    def add_column(self, name, default=''):
        self.colNames.add(name, default)
        for row in self.rows:
            row.append(default)

    def del_column(self, name):
        if name not in self.colNames:
            raise Exception("This column don't exits : " + name)
        else:
            i = self.colNames[name]
            for row in self.rows:
                del row[i]
            self.colNames.delete(name)

    def _new_row(self, **kwargs):
        row = Row(self.colNames.defaults, self.colNames)
        for key, value in kwargs.items():
            row[self.colNames[key]] = value
        return row

    def append(self, **kwargs):
        self.rows.append(self._new_row(**kwargs))

    def insert(self, i, **kwargs):
        self.rows.insert(i, self._new_row(**kwargs))

    def __iter__(self):
        return self.rows.__iter__()

    def __reversed__(self):
        return self.rows.__reversed__()

    def __delitem__(self, index):
        del self.rows[index]

    def __getitem__(self, index):
        return self.rows[index]

    def __len__(self):
        return len(self.rows)

    def __repr__(self):
        ch = '  col  : ['
        idx = 0
        lst = self.colNames.sorted()
        print(lst)
        for col in lst:
            ch += "'" + col[0] + "', "
        ch = regexp.sub(', $', '', ch) + ']\n'
        for row in self.rows:
            line = ''
            for col in row:
                line += col.__repr__() + ', '
            ch += '  row ' + str(idx) + ': [' + regexp.sub(', $', '',
                                                           line) + ']\n'
            idx += 1
        return '[\n' + ch + ']'

    def features_by_label(self):
        if len(self.unique('show')) > 1:
            raise Exception('table address sevreal shows')
        d = dict()
        for row in self.rows:
            label = row['label']
            start = row['start']
            stop = row['stop']

            if label not in d:
                d[label] = []

            d[label] += [i for i in range(start, stop)]
        return d

    def pack(self, epsilon=0):
        self.sort(['start'])
        i = 0
        while i < len(self.rows) - 1:
            if self.rows[i]['show'] == \
                    self.rows[i + 1]['show'] and \
                    self.rows[i]['label'] == self.rows[i + 1]['label'] and \
                    Row.gap(self.rows[i], self.rows[i + 1]).length() < epsilon:
                self.rows[i]['stop'] = self.rows[i + 1]['stop']
                del self.rows[i + 1]
            else:
                i += 1


    @classmethod
    def read_seg(cls, filename):
        fic = open(filename, 'r')
        table = Table()
        for line in fic:
            line = line.strip()
            if line.startswith('#') or line.startswith(';;'):
                continue
            # split line into fields
            show, start, stop, label_type, name = line.split()
            stop = int(round(float(stop) * 100))
            start = int(round(float(start) * 100))
#            logging.info('%s; %s; %s; %s; %s;', show, start, stop, label_type, name)
            table.append(show=show, start=start, stop=stop, labelType=label_type,
                        label=name)
        fic.close()
        return table

    @classmethod
    def to_string_seg(cls, table):
        lst = []
        for row in table:
            if table.colNames.exist('channel'):
                channel = row['channel']
            lst.append('{:s} {:d} {:d} {:s} {:s}\n'.format(
                row['show'], row['start']/100, row['stop']/100, row['labelType'], row['label']))
        return lst

    @classmethod
    def write_seg(cls, filename, table):
        table.sort(['show', 'start'])
        fic = open(filename, 'w')
        for line in Table.to_string_seg(table):
            fic.write(line)
        fic.close()


def error(ref, hyp):
    idx_ref = list()
    for r in ref:
        idx_ref += [x for x in range(r['start'], r['stop'])]

    idx_hyp = list()
    for h in hyp:
        idx_hyp += [x for x in range(h['start'], h['stop'])]


    inter = set(idx_hyp) & set(idx_ref)
    correct = len(inter)
    error = len(idx_ref) - correct

#    print(match, miss, fa)

    return correct, error

def by_coll(ref_coll, hyp_coll):
    idx_ref = ref_coll.make_index(['label', 'show'])
    idx_hyp = hyp_coll.make_index(['label', 'show'])
    fcorrect, ferror, ftot = 0, 0, 0
    for label in idx_ref:
        scorrect, serror, stot = 0, 0, 0
        for show in idx_ref[label]:
            r = idx_ref[label][show]
            h = list()
            if label in idx_hyp and show in idx_hyp[label]:
                h = idx_hyp[label][show]
            match, miss = error(r, h)
            scorrect += match
            serror += miss
            stot += miss + match
        logging.info('spk : %s correct: %f error: %f (%.2f s.)', label, scorrect/stot*100, serror/stot*100, stot/100)
        fcorrect += scorrect
        ferror += serror
        ftot += stot
    logging.info('-' * 80)
    logging.info('sum correct: %f error: %f (%.2f s.)', fcorrect/ftot*100, ferror/ftot*100, ftot/100)


def main():
    logging.basicConfig(
        format='%(module)s:%(funcName)s:%(lineno)d: %(message)s',
        level=logging.INFO)
    logging.info('-' * 80)
    parser = argparse.ArgumentParser(description='Diarization for ASR')
    parser.add_argument('input_ref', help='input')
    parser.add_argument('input_hyp', help='input')
    args = parser.parse_args()

    logging.info('read ref and hyp')
    ref = Table.read_seg(args.input_ref)
    hyp = Table.read_seg(args.input_hyp)

    stat = dict()

    logging.info('get index')
    index = ref.make_index(['label', 'show'])
    for label in index:
        for show in index[label]:
            if not label.startswith('speaker#') and not label.startswith('inconnu_') and not label.startswith('Inconnu_'):
                if label in stat:
                    stat[label] += 1
                else:
                    stat[label] = 1
    logging.info('-' * 80)
    v = np.array(stat.values())
    k = np.array(stat.keys())
    m = np.max(v)
    # plt.hist(v, range(m))
    # plt.xlabel("Speaker in x shows")
    # plt.ylabel("Frequency")
    # plt.show()
    # print(stat)

    ns = (v > 1).sum()
    ni = (v <= 1).sum()
    logging.info("nombre de locuteur dans plus d'un show : %d (%.2f per)", ns , ns/len(v)*100)
    logging.info("nombre de locuteur dans un show : %d (%.2f per)", ni , ni/len(v)*100)

    label_coll = list()
    label_ncoll = list()
    for key, value in stat.iteritems():
        if value > 1:
            label_coll.append(key)
        else:
            label_ncoll.append(key)

    ref_coll = ref.filter('label', 'in', label_coll.__repr__())
    hyp_coll = hyp.filter('label', 'in', label_coll.__repr__())
    ref_ncoll = ref.filter('label', 'in', label_ncoll.__repr__())
    hyp_ncoll = hyp.filter('label', 'in', label_ncoll.__repr__())

    d_coll = 0
    for row in ref_coll:
        d_coll += (row['stop'] - row['start'])/100

    d_ncoll = 0
    for row in ref_ncoll:
        d_ncoll += (row['stop'] - row['start'])/100

    logging.info("duree des locuteurs dans plus d'un show : %d s. (%.2f per)", d_coll , d_coll/(d_coll+d_ncoll))
    logging.info("duree des locuteurs dans un show : %d s. (%.2f per)", d_ncoll , d_ncoll/(d_coll+d_ncoll))


    logging.info('=' * 80)
    logging.info("ERREUR pour les locuteurs dans plus d'un show")
    by_coll(ref_coll, hyp_coll)

    logging.info('=' * 80)
    logging.info("ERREUR pour les locuteurs dans un show")
    by_coll(ref_ncoll, hyp_ncoll)

    # logging.info('=' * 80)
    # logging.info("ERREUR pour tous les locuteurs")
    # by_coll(ref, hyp)

if __name__ == "__main__":
    # execute only if run as a script
    main()