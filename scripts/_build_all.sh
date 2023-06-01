#!/bin/bash
#
#    _build_all.sh
#
# prepare all quran data structure for rasm
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
#   $ bash _build_all.sh -f
#
################################################################################

MYDIR=$(dirname "$0")

TANZIL_SIMPLE_INPUT="$MYDIR"/../rasm_arch/resources/quran-simple.txt
TANZIL_UTHMANI_INPUT="$MYDIR"/../rasm_arch/resources/quran-uthmani.txt
DECOTYPE_INPUT="$MYDIR"/../../../abjad/abjad_util/data/processed/mushaf.json

TANZIL_SIMPLE_OUTPUT="$MYDIR"/../rasm_arch/resources/mushaf_simple.json
TANZIL_UTHMANI_OUTPUT="$MYDIR"/../rasm_arch/resources/mushaf_uthmani.json
DECOTYPE_OUTPUT="$MYDIR"/../rasm_arch/resources/mushaf_dt.json

HELP='\n'\
'usage:\n'\
"\tbash $0 [options]\n"\
'\n'\
'options:\n'\
'\t-f    force build of resources'\
'\n'

OPTIND=1  # POSIX variable, reset in case getopts has been used previously in the shell.
FORCE_FLAG=0

parse_arguments()
{
  while getopts ':hf' opt
  do
    case "$opt" in
      'h') echo -e "$HELP" ; exit 0 ;;
      'f') FORCE_FLAG=1 ;;
      '?') echo -e "\n${RED_COLOR} option -$OPTARG not valid${END_COLOR}\n$HELP" >&2 ; exit 1 ;;
    esac
  done

  shift $((OPTIND-1))
  [ "$1" = "--" ] && shift
}

parse_arguments $@

if [[ ! -f $TANZIL_SIMPLE_OUTPUT || $FORCE_FLAG -eq 1 ]] ; then
    cat $TANZIL_SIMPLE_INPUT | python "$MYDIR"/_build_qstruct.py > $TANZIL_SIMPLE_OUTPUT ;
    echo "tanzil simple processed!" >/dev/stderr
fi &&

if [[ ! -f $TANZIL_UTHMANI_OUTPUT || $FORCE_FLAG -eq 1 ]] ; then
    cat $TANZIL_UTHMANI_INPUT | python "$MYDIR"/_build_qstruct.py > $TANZIL_UTHMANI_OUTPUT ;
    echo "tanzil uthmani processed!" >/dev/stderr
fi  &&

if [[ ! -f $DECOTYPE_OUTPUT || $FORCE_FLAG -eq 1 ]] ; then
    if [ -f $DECOTYPE_INPUT ] ; then
        cat $DECOTYPE_INPUT | python "$MYDIR"/_build_qstruct_dt.py > $DECOTYPE_OUTPUT ;
        echo "decotype processed!"
    fi
fi
