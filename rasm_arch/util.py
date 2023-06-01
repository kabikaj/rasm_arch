#!/user/bin/env python3
#
#    util.py
#
# utility data structures and functions
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
###################################################################################

from dataclasses import dataclass

@dataclass
class SOURCE:
    TANZIL_SIMPLE = 'mushaf_simple.json'
    TANZIL_UTHMANI = 'mushaf_uthmani.json'
    DECOTYPE = 'mushaf_dt.json'

class PrivateFileError(FileNotFoundError):
    """Exception raised when resources file is not found

    Attributes:
        msg (str): explanation of the error

    """

    def __init__(self, message='Decotype Quran is private.'):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

ABJAD_MAPPING = {
    'Q' : 'ٯ' ,
    'N' : 'ں' ,
    'Y' : 'ی' ,
    'B' : 'ٮ' ,
    'G' : 'ح' ,
    'T' : 'ط' ,
    'C' : 'ص' ,
    'S' : 'س' ,
    'F' : 'ڡ' ,
    'E' : 'ع' ,
    'H' : 'ه' ,
    'M' : 'م' ,
    'L' : 'ل' ,
    'K' : 'ك' ,
    'A' : 'ا' ,
    'R' : 'ر' ,
    'D' : 'د' ,
    'W' : 'و' ,
}

def _nest(*functs):
    """ Nest calls to generators recursively.

    Args:
        functs (tuple): sequence of generators to nest.

    Yields:
        generator: nested calls to all generators included in functs.

    """
    f1, *functs = functs
    n = len(functs)
    if n == 0:
        return f1
    elif n == 1:
        return functs[0](f1)
    else:
        f2, *functs = functs
        return _nest(f2(f1), *functs)

def pipe(stream, *process):
    """ Apply sequence of processes to stream.

    Args:
        stream (iterator): data to pass through sequence of processes.
        process (tuple): function to apply to data.

    Yields:
        iterator: nested calls to processes over stream, or stream in case process is empty.

    """
    f1, *functs = process
    yield from stream if not f1 else _nest(f1(stream), *functs)

