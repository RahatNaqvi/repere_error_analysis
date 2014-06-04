#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE S PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# AUTHORS
# Hervé BREDIN (http://herve.niderb.fr)

from pyannote.parser.trs import TRSParser
from pyannote.parser.repere import REPEREParser


with open('../data/shows.txt', 'r') as f:
    uris = [show.strip() for show in f]

repere = REPEREParser()

with open('../data/reference.repere', 'w') as f:

    for u, uri in enumerate(uris):

        print '{u:d}/{n:d}: {uri:s}'.format(u=u, n=len(uris), uri=uri)

        # load speaker annotation
        trs = TRSParser().read('../data/trs/{uri}.trs'.format(uri=uri))
        speaker = trs(uri=uri, modality='speaker')

        # save it back to file in REPERE format
        repere.write(speaker, f=f)
