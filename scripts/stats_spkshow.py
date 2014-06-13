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

# load parser for files in REPERE submissions format
from pyannote.parser.repere import REPEREParser
# load parser for UEM files
from pyannote.parser.uem import UEMParser
# load identification error analysis tool
from pyannote.metrics.errors.identification import IdentificationErrorAnalysis


def analyse_ier(references, hypotheses, uems,
                uris=None, collar=0., unknown=True):
    """

    Parameters
    ----------
    references : `REPEREParser`
    hypotheses : dict of `REPEREParser`
        Dictionary keys are names of consortia.
    uems : `UEMParser`
    uris : iterable, optional
        When provided, only perform evaluation on those shows.
    collar : float, optional
        Collar (in ms) centered on reference boundaries.
        Defaults to no collar.
    unknown : bool, optional
        Keep unknown. Defaults to True.

    Returns
    -------
    analysis : dict of dict of DataFrame
        Consortia-indexed dictionary of show-indexed dictionary accumulated
        identification errors.
    """

    # get list of consortia in alphabetical order
    consortia = sorted(hypotheses)

    # defaults to all show in reference
    if uris is None:
        uris = references.uris

    identificationErrorAnalysis = IdentificationErrorAnalysis(collar=collar,
                                                              unknown=unknown)

    analysis = {team: dict() for team in consortia}

    # loop on every show (uri stands for 'uniform resource identifier')
    for u, uri in enumerate(uris):

        # get UEM for current show
        uem = uems(uri=uri)

        # get reference for this very show
        reference = references(uri=uri, modality='speaker')

        # get hypothesis for this very show for all three consortia
        hypothesis = {
            team: hypotheses[team](uri=uri, modality='speaker')
            for team in consortia
        }

        # analyse errors for each team
        for team in consortia:
            analysis[team][uri] = identificationErrorAnalysis.matrix(
                reference, hypothesis[team], uem=uem)

    return analysis


# load reference (see trs2repere.py)
references = REPEREParser().read('../data/reference.repere')

# load uem
uems = UEMParser().read('../data/test2.uem')

# load PRIMARY runs for all 3 consortia
consortia = ['percol', 'qcompere', 'soda']
hypotheses = {
    team: REPEREParser().read('../data/{team}.repere'.format(team=team))
    for team in consortia}

analysis = analyse_ier(references, hypotheses, uems,
                       uris=None, collar=0., unknown=False)

template = "{uri} {spk} {ref:.2f} {hyp:.2f} {cor:.2f} {miss:.2f} {fa:.2f}\n"

for team in consortia:

    with open('../data/{team}.stats'.format(team=team), 'w') as f:

        for uri in references.uris:
            M = analysis[team][uri]
            speakers = [speaker for speaker in M.get_rows()]
            for spk in speakers:

                if isinstance(spk, tuple) and spk[0] == 'false alarm':
                    continue

                ref = M[spk, 'reference']
                hyp = M[spk, 'hypothesis']
                cor = M[spk, 'correct']
                miss = M[spk, 'missed detection']
                fa = M[spk, 'false alarm']

                f.write(template.format(uri=uri, spk=spk, ref=ref, hyp=hyp,
                                        cor=cor, miss=miss, fa=fa))

