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
Segment-wise statistics

This tool outputs various statistics for each reference segment (one per line).
It uses the following format:

    - Field #1: show
    - Field #2: segment start time (in seconds)
    - Field #3: segment end time (in seconds)
    - Field #4: speaker label
    - Field #5: segment identification error rate
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
  --with-unknown           Keep unknown in evaluation.
  -h --help                Show this screen.
  --version                Show version.
"""

TEMPLATE = "{uri} {start:.3f} {end:.3f} {spk} {ier:.3f} {cor:.2f} {conf:.2f} {miss:.2f} {fa:.2f}\n"

import sys

# command line argument parser
from docopt import docopt

# file parser
from pyannote.parser.util import CoParser

#
from pyannote.core import Annotation, Unknown

# identification error rate
from pyannote.metrics.identification import IdentificationErrorRate, \
    IER_CORRECT, IER_CONFUSION, IER_FALSE_ALARM, IER_MISS, IER_NAME


def do_stats(reference_repere, hypothesis_repere,
             uris_lst=None, eval_uem=None,
             unknown=False):

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

    identificationErrorRate = IdentificationErrorRate(unknown=unknown)

    for uri, ref, hyp, uem in coParser.iter(
        'uris', 'reference', 'hypothesis', 'uem'
    ):

        ref = ref.crop(uem, mode='intersection')
        hyp = hyp.crop(uem, mode='intersection')

        overlap = {}

        # starts by finding overlap regions in reference
        # this will iterate over all pairs of intersecting segments
        for (segment, track), (segment_, track_) in ref.co_iter(ref):

            # do not count twice
            if (segment, track) >= (segment, track_):
                continue

            # overlap duration
            intersection = (segment & segment_).duration

            # increment overlap count
            overlap[segment, track] = \
                overlap.get((segment, track), 0.) + intersection
            overlap[segment_, track_] = \
                overlap.get((segment_, track_), 0.) + intersection

        for segment, _, spk in ref.itertracks(label=True):

            if isinstance(spk, Unknown):
                continue

            r = Annotation(uri=ref.uri, modality=ref.modality)
            r[segment] = spk

            h = hyp.crop(segment)

            details = identificationErrorRate(r, h, detailed=True)
            ovr = overlap.get((segment, track), 0)
            ier = details[IER_NAME]
            cor = details[IER_CORRECT]
            conf = details[IER_CONFUSION] - 0.5 * ovr
            miss = details[IER_MISS] + .5 * ovr
            fa = details[IER_FALSE_ALARM]

            sys.stdout.write(
                TEMPLATE.format(uri=uri, start=segment.start, end=segment.end,
                                spk=spk, ier=ier, cor=cor, conf=conf, miss=miss,
                                fa=fa))

            sys.stdout.flush()


if __name__ == '__main__':

    arguments = docopt(__doc__)

    reference_repere = arguments['<references.repere>']
    hypothesis_repere = arguments['<hypothesis.repere>']
    eval_uem = arguments['<eval.uem>']
    uris_lst = arguments['--uris']
    unknown = arguments['--with-unknown']

    do_stats(reference_repere, hypothesis_repere,
             uris_lst=uris_lst, eval_uem=eval_uem,
             unknown=unknown)
