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

"""
Speaker/Show statistics

This tool outputs various statistics for each show/speaker pair (one per line).
It uses the following format:

    - Field #1: show
    - Field #2: speaker
    - Field #3: identification error rate
    - Field #4: total speech duration in reference
    - Field #5: total speech duration in hypothesis
    - Field #6: duration of correct identification
    - Field #7: duration of confusion
    - Field #8: duration of missed detections
    - Field #9: duration of false alarms

Usage:
  stats [options] <references.repere> <eval.uem> <hypothesis.repere>
  stats -h | --help
  stats --version

Options:
  --uris <uris.lst>        List of shows (one per line).
                           Defaults to the list of shows in reference.
  --collar <duration>      Collar (in seconds) removed from evaluation around
                           boundaries of reference segments [default: 0.]
  --with-unknown           Keep unknown in evaluation.
  -h --help                Show this screen.
  --version                Show version.
"""

TEMPLATE = "{uri} {spk} {ier:.3f} {ref:.2f} {hyp:.2f} {cor:.2f} {conf:.2f} {miss:.2f} {fa:.2f}\n"


import sys

# command line argument parser
from docopt import docopt

# file parser
from pyannote.parser.util import CoParser

# identification error analysis
from pyannote.metrics.errors.identification import IdentificationErrorAnalysis


def do_stats(reference_repere, hypothesis_repere,
             uris_lst=None, eval_uem=None,
             collar=0., unknown=False):

    identificationErrorAnalysis = IdentificationErrorAnalysis(
        collar=collar, unknown=unknown)

    iter_over = {
        'reference': reference_repere,
        'hypothesis': hypothesis_repere
    }

    if uris_lst:
        iter_over['uris'] = uris_lst
    else:
        iter_over['uris'] = 'reference'

    if eval_uem:
        iter_over['uem'] = eval_uem

    coParser = CoParser(**iter_over)

    for uri, ref, hyp, uem in coParser.iter(
        'uris', 'reference', 'hypothesis', 'uem'
    ):

        # perform error analysis
        analysis = identificationErrorAnalysis.matrix(ref, hyp, uem=uem)

        # obtain list of speakers
        speakers = [speaker for speaker in analysis.get_rows()]

        # loop on each speaker
        for spk in speakers:

            if isinstance(spk, tuple) and spk[0] == 'false alarm':
                continue

            ref = analysis[spk, 'reference']
            hyp = analysis[spk, 'hypothesis']
            cor = analysis[spk, 'correct']
            conf = analysis[spk, 'confusion']
            miss = analysis[spk, 'missed detection']
            fa = analysis[spk, 'false alarm']
            ier = (conf + miss + fa) / ref

            sys.stdout.write(
                TEMPLATE.format(uri=uri, spk=spk, ier=ier, ref=ref, hyp=hyp,
                                cor=cor, conf=conf, miss=miss, fa=fa))

            sys.stdout.flush()

if __name__ == '__main__':

    arguments = docopt(__doc__)

    reference_repere = arguments['<references.repere>']
    hypothesis_repere = arguments['<hypothesis.repere>']
    eval_uem = arguments['<eval.uem>']
    uris_lst = arguments['--uris']
    collar = float(arguments['--collar'])
    unknown = arguments['--with-unknown']

    do_stats(reference_repere, hypothesis_repere,
             uris_lst=uris_lst, eval_uem=eval_uem,
             collar=collar, unknown=unknown)
