# Rasm

> Rasm is a text processing utility for converting Arabic-scripted text to a completely dediacritised skeleton.

<img src="./rasm.png" align="middle">

Rasm is a text processing utility for converting Arabic-scripted text to a completely dediacritised skeleton. If Quranic indexes are given, it can also retrieve Quranic text.

A minimal Rust implementation can be found under src.

## Requirements

setuptools==59.1.1 \
ujson==5.1.0

If ujson is not installed, json will be used.

## Installation

Use the makefile to install th rasm package:

```sh
$ make install
```

Use the following commands to uninstall it:

```sh
$ python setup.py install --record files.txt
$ xargs rm -rf < files.txt
```

## Examples of usage

In python:

```sh
>>> import io
>>> from rasm import rasm
>>> for ori, rlt, rar, pal in rasm(io.StringIO('کُتِب'), paleo=True):
...   print(ori, rlt, rar, pal)
کُتِب KBB كٮٮ KᵘB²ᵢB₁

```

```sh
>>> import io
>>> from rasm import rasm
>>> for word, blocks in rasm(((2, 14,15, None), (2, 15, 1, 1)), paleo=True, blocks=True):
...   print(word, *blocks[0], sep='\t')
...   if len(blocks)>1:
...     for block in blocks[1:]:
...         print('-', *block, sep='\t')
نَحۡنُ      نَحۡنُ    BGN   ٮحں   B¹ᵃGᵒN¹ᵘ       (2, 14, 15, 1)
مُسۡتَهۡزِءُونَ مُسۡتَهۡزِءُ MSBHR مسٮهر MᵘSᵒB²ᵃHᵒR¹ᵢʔᵘ (2, 14, 16, 1)
-        و      W     و     W              (2, 14, 16, 2)
-        نَ      N     ں     N¹ᵃ            (2, 14, 16, 3)
ٱ        ٱ      A     ا     Aᵟ              (2, 15, 1, 1)
```

As a bash command:

```sh
>>> aspell -d ar dump master | rasm | tail -2
يين  BBN  ٮٮں
ييئس BBBS ٮٮٮس
```

```sh
>>> rasm -q 2:1:4-2:1:5:1 --uniq --json | jq .
[
  {
    "ori": "A",
    "rlt": "ا",
    "rar": 2,
    "frq": [
      "ٱلرَّحِیمِ",
      "ا"
    ]
  },
  {
    "ori": "GBM",
    "rlt": "حٮم",
    "rar": 1,
    "frq": [
      "ٱلرَّحِیمِ"
    ]
  },
  {
    "ori": "LR",
    "rlt": "لر",
    "rar": 1,
    "frq": [
      "ٱلرَّحِیمِ"
    ]
  }
]
```

## Version

This version requires Python 3.8 or later.

## License for the code
 
Rasm is a text processing utility for converting Arabic-scripted text to a completely dediacritised skeleton.

The code for this project is licensed under the MIT License.

Be aware that if you use the Quranic text from rasm, they have two different licences, that you can find below.

MIT License

Copyright (c) 2022 Alicia González Martínez and Thomas Milo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## License for the data

Rasm includes two digitised Quranic texts: The Decotype Quran and the Tanzil Quran.

### Decotype Quran

The Decotype Quran is the best encoded Quran with complete orthography and the only one approved by Al-Azhar until now.

....

### Tanzil Quran

The Tanzil Quran is the most widely used digital Quran. It was made available by the Tanzil project, https://tanzil.net.

We have included two versions of the Tanzil Quran text:
- A complete Uthmanic Quran
- A simplified Quran

Tanzil Quran Text 
  Copyright (C) 2007-2021 Tanzil Project
  License: Creative Commons Attribution 3.0 

  This copy of the Quran text is carefully produced, highly 
  verified and continuously monitored by a group of specialists 
  in Tanzil Project.

  TERMS OF USE:
 
  - Permission is granted to copy and distribute verbatim copies 
    of this text, but CHANGING IT IS NOT ALLOWED.

  - This Quran text can be used in any website or application, 
    provided that its source (Tanzil Project) is clearly indicated, 
    and a link is made to tanzil.net to enable users to keep
    track of changes.

  - This copyright notice shall be included in all verbatim copies 
    of the text, and shall be reproduced appropriately in all files 
    derived from or containing substantial portion of this text.

  Please check updates at: http://tanzil.net/updates/

## Contact

Alicia González Martínez , *aliciagm85+kabikaj at gmail dot com*

