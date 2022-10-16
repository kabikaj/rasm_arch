#!/usr/bin/env python3
#
#    _build_qstruct.py
#
# create quran data struct based on tanzil quran for rasm package
# 
# quranic texts downloaded from https://tanzil.net/download
#   quran-simple.txt - no options selected
#   quran-uthmani.txt - Include pausal marks, Include sajdah signs (۩), Include rub-el-hizb signs (۞)
#
# MIT License
# 
# Copyright (c) 2022 Alicia González Martínez and Thomas Milo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# usage:
#   $ cat ../resources/quran-simple.txt | python _build_qstruct.py > ../resources/mushaf_simple.json
#   $ cat ../resources/quran-uthmani.txt | python _build_qstruct.py > ../resources/mushaf_uthmani.json
#
#######################################################################################################

import io
import re
import sys
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from argparse import ArgumentParser, FileType

from rasm import rasm

STRUCT = {'tok' : [],  # [(tok, pal), ... ] 
          'ind' : [],  # [[[[itok, ... ], ...], ...], ...] # sura[vers][word][block] ; +1 to calculate the real index
}

def _fix(s):
    s = re.sub(r' ([ۣۜۖۗۘۙۚۛ])', r'\1', s)
    return s

def proc_quran(fp):
    """ parse tanzil quran, split in blocks keeping indexes and retrieve together with rasm conversion.

    Args:
        fp(io.TextIOWrapper): stream to read tanzil quran.

    yield:
        sura(int), vers(int), word(int), block(int), text(str): full index and content of block in tanzil quran.

    """
    entries = (li.split('|', 2) for li in filter(None, (l.strip() for l in fp)) if li[0]!='#')
    yield from ((tok, int(s), int(v), w) for s, v, text in entries for w, tok in enumerate(_fix(text).split(), 1))


if __name__ == '__main__':

    parser = ArgumentParser(description='prepare tanzil quran the rasm package')
    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin, help='tanzil quran')
    parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout, help='processed quran')
    args = parser.parse_args()

    pre_sura, pre_vers, pre_word = -1, -1, -1
    for word_tok, sura, vers, word in proc_quran(args.infile):

        blocks_groups = [bks for _, bks in rasm(io.StringIO(word_tok), paleo=True, blocks=True)]

        # ۞ ۩
        if not blocks_groups[0]:
            blocks_groups=[[(word_tok, '', '')]]

        for blocks in blocks_groups:

            for bloc_tok, *_, pal in blocks:

                if (bloc_tok, pal) in STRUCT['tok']:
                    i = STRUCT['tok'].index((bloc_tok, pal))
                else:
                    STRUCT['tok'].append((bloc_tok, pal))
                    i = len(STRUCT['tok'])-1
        
                if pre_sura != sura:
                    STRUCT['ind'].append([[[i]]])
                else:
                    if pre_vers != vers:
                        STRUCT['ind'][-1].append([[i]])
                    else:
                        if pre_word != word:
                            STRUCT['ind'][-1][-1].append([i])
                        else:
                            STRUCT['ind'][-1][-1][-1].append(i)
        
                pre_sura, pre_vers, pre_word = sura, vers, word

    json.dump(STRUCT, args.outfile)
