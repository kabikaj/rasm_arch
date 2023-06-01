#!/usr/bin/env python3
#
#    rasm_arch.py
#
# convert arabic script to archigraphemes
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
################################################################################

import re
import sys
try:
    import ujson as json
except ImportError:
    import json

from io import TextIOBase
from string import whitespace, punctuation
from functools import partial, singledispatch
from importlib.resources import files
from dataclasses import dataclass
from itertools import groupby

from rasm_arch.util import SOURCE, ABJAD_MAPPING, PrivateFileError, pipe

@dataclass
class DATA:
    """ Inventory of characters in the Arabic abjad.

    """
    Q = 'ٯࢥڧقڨﻕﻖ'
    N = 'ںنڻڼڹݧݨݩڽﻥﻦ'
    Y = 'ىیۍݷيېۑؠئؽێݵݶࢨࢩؾؿےۓݺݻﻯﻰﮮﮯﯼﯽﻲﮰﮱﺉﺊ'
    A = 'ٱأإآاٳٲݳݴٵﺃﺄﺇﺈﺁﺂﺍﺎﭐﭑﴼ'
    B = 'ࢬٮبݕࢠٻݐپڀݒٹݖݔتٺټݓثٽٿݑﻧﻨﯾﯿﻳﻴﺋﺌﺏﺐﺑﺒﭖﭗﭘﭙﺕﺖﺗﺘﺙﺚﺛﺜ'
    G = 'خحجچݮݼڃڄچڇݘݯځݲڿڂݗࢢڅﺝﺞﺟﺠﺡﺢﺣﺤﺥﺦﺧﺨﭺﭻﭼﭽ'
    R = 'رزړݛࢪڔڕڑڒۯݬږڗݫژڙݱﺭﺮﺯﺰﮊﮋ'
    D = 'دذڈډڊݚڍڈۮڋݙڌڎڏڐﺩﺪﺫﺬ'
    T = 'طظࢣڟﻁﻂﻃﻄﻅﻆﻇﻈ'
    C = 'صضڝۻڞﺹﺺﺻﺼﺽﺾﺿﻀ'
    S = 'سشڛݽݾښݭݜݰۺڜﺱﺲﺳﺴﺵﺶﺷﺸ'
    F = 'فﻑﻒڡڢݠڥݡڣڤڦࢤﻓﻔﻗﻘ'
    E = 'عغۼݝݟڠݞﻉﻊﻋﻌﻍﻎﻏﻐ'
    W = 'وۄۅࢫؤۆۇۈۉۏݸݹۊۋﻭﻮﺅﺆ'
    H = 'هھہەۀۂۿةۃﮤﮥﺓﺔﮦﮧﮨﮩﻪﻫﻬﮪﮫﮬﮭ'
    M = 'مݦݥࢧﻡﻢﻣﻤ'
    L = 'لݪࢦڸڵڶڷﻝﻞﻟﻠ'
    K = 'كکڪګگڰڲڳؼڮݤݢػڱݿڭڴݣﻙﻚﻛﻜﮎﮏﮐﮑﮒﮓﮔﮕ'

    CHAR = ''.join((Q, N, Y, A, B, G, R, D, T, C, S, F, E, W, H, M, L, K))
    
    RASM_QNY_MAPPING = {
        ** {c : 'Q' for c in Q},
        ** {c : 'N' for c in N},
        ** {c : 'Y' for c in Y},
    }

    RASM_MAPPING = {
        ** {c : 'B' for c in ''.join((N, Y, B))},
        ** {c : 'G' for c in G},
        ** {c : 'T' for c in T},
        ** {c : 'C' for c in C},
        ** {c : 'S' for c in S},
        ** {c : 'F' for c in ''.join((Q, F))},
        ** {c : 'E' for c in E},
        ** {c : 'H' for c in H},
        ** {c : 'M' for c in M},
        ** {c : 'L' for c in L},
        ** {c : 'K' for c in K},
        ** {c : 'A' for c in A},
        ** {c : 'R' for c in R},
        ** {c : 'D' for c in D},
        ** {c : 'W' for c in W}
    }

    NORM_MAPPING = {
        'ََ': 'ً',
        'ُُ': 'ٌ',
        'ِِ': 'ٍ',
    }

    NORM_REGEX = re.compile('|'.join(NORM_MAPPING))
    
    CLUSTERS = {
        "ﯪ" : "ئا",
        "ﯫ" : "ئا",
        "ﯬ" : "ئە",
        "ﯭ" : "ئە",
        "ﯮ" : "ئو",
        "ﯯ" : "ئو",
        "ﯰ" : "ئۇ",
        "ﯱ" : "ئۇ",
        "ﯲ" : "ئۆ",
        "ﯳ" : "ئۆ",
        "ﯴ" : "ئۈ",
        "ﯵ" : "ئۈ",
        "ﯶ" : "ئې",
        "ﯷ" : "ئې",
        "ﯸ" : "ئې",
        "ﯹ" : "ئى",
        "ﯺ" : "ئى",
        "ﯻ" : "ئى",
        "ﰃ" : "ئى",
        "ﱨ" : "ئى",
        "ﰀ" : "ئج",
        "ﲗ" : "ئج",
        "ﰁ" : "ئح",
        "ﲘ" : "ئح",
        "ﰂ" : "ئم",
        "ﱦ" : "ئم",
        "ﲚ" : "ئم",
        "ﳟ" : "ئم",
        "ﰄ" : "ئي",
        "ﱩ" : "ئي",
        "ﰅ" : "بج",
        "ﲜ" : "بج",
        "ﰆ" : "بح",
        "ﲝ" : "بح",
        "ﰇ" : "بخ",
        "ﲞ" : "بخ",
        "ﰈ" : "بم",
        "ﱬ" : "بم",
        "ﲟ" : "بم",
        "ﳡ" : "بم",
        "ﰉ" : "بى",
        "ﱮ" : "بى",
        "ﰊ" : "بي",
        "ﱯ" : "بي",
        "ﰋ" : "تج",
        "ﲡ" : "تج",
        "ﰌ" : "تح",
        "ﲢ" : "تح",
        "ﰍ" : "تخ",
        "ﲣ" : "تخ",
        "ﰎ" : "تم",
        "ﱲ" : "تم",
        "ﲤ" : "تم",
        "ﳣ" : "تم",
        "ﰏ" : "تى",
        "ﱴ" : "تى",
        "ﰐ" : "تي",
        "ﱵ" : "تي",
        "ﰑ" : "ثج",
        "ﰒ" : "ثم",
        "ﱸ" : "ثم",
        "ﲦ" : "ثم",
        "ﳥ" : "ثم",
        "ﰓ" : "ثى",
        "ﱺ" : "ثى",
        "ﰔ" : "ثي",
        "ﱻ" : "ثي",
        "ﰕ" : "جح",
        "ﲧ" : "جح",
        "ﰖ" : "جم",
        "ﲨ" : "جم",
        "ﰗ" : "حج",
        "ﲩ" : "حج",
        "ﰘ" : "حم",
        "ﲪ" : "حم",
        "ﰙ" : "خج",
        "ﲫ" : "خج",
        "ﰚ" : "خح",
        "ﰛ" : "خم",
        "ﲬ" : "خم",
        "ﰜ" : "سج",
        "ﲭ" : "سج",
        "ﴴ" : "سج",
        "ﰝ" : "سح",
        "ﲮ" : "سح",
        "ﴵ" : "سح",
        "ﰞ" : "سخ",
        "ﲯ" : "سخ",
        "ﴶ" : "سخ",
        "ﰟ" : "سم",
        "ﲰ" : "سم",
        "ﳧ" : "سم",
        "ﰠ" : "صح",
        "ﲱ" : "صح",
        "ﰡ" : "صم",
        "ﲳ" : "صم",
        "ﰢ" : "ضج",
        "ﲴ" : "ضج",
        "ﰣ" : "ضح",
        "ﲵ" : "ضح",
        "ﰤ" : "ضخ",
        "ﲶ" : "ضخ",
        "ﰥ" : "ضم",
        "ﲷ" : "ضم",
        "ﰦ" : "طح",
        "ﲸ" : "طح",
        "ﰧ" : "طم",
        "ﴳ" : "طم",
        "ﴺ" : "طم",
        "ﰨ" : "ظم",
        "ﲹ" : "ظم",
        "ﴻ" : "ظم",
        "ﰩ" : "عج",
        "ﲺ" : "عج",
        "ﰪ" : "عم",
        "ﲻ" : "عم",
        "ﰫ" : "غج",
        "ﲼ" : "غج",
        "ﰬ" : "غم",
        "ﲽ" : "غم",
        "ﰭ" : "فج",
        "ﲾ" : "فج",
        "ﰮ" : "فح",
        "ﲿ" : "فح",
        "ﰯ" : "فخ",
        "ﳀ" : "فخ",
        "ﰰ" : "فم",
        "ﳁ" : "فم",
        "ﰱ" : "فى",
        "ﱼ" : "فى",
        "ﰲ" : "في",
        "ﱽ" : "في",
        "ﰳ" : "قح",
        "ﳂ" : "قح",
        "ﰴ" : "قم",
        "ﳃ" : "قم",
        "ﰵ" : "قى",
        "ﱾ" : "قى",
        "ﰶ" : "قي",
        "ﱿ" : "قي",
        "ﰷ" : "كا",
        "ﲀ" : "كا",
        "ﰸ" : "كج",
        "ﳄ" : "كج",
        "ﰹ" : "كح",
        "ﳅ" : "كح",
        "ﰺ" : "كخ",
        "ﳆ" : "كخ",
        "ﰻ" : "كل",
        "ﲁ" : "كل",
        "ﳇ" : "كل",
        "ﳫ" : "كل",
        "ﰼ" : "كم",
        "ﲂ" : "كم",
        "ﳈ" : "كم",
        "ﳬ" : "كم",
        "ﰽ" : "كى",
        "ﲃ" : "كى",
        "ﰾ" : "كي",
        "ﲄ" : "كي",
        "ﰿ" : "لج",
        "ﳉ" : "لج",
        "ﱀ" : "لح",
        "ﳊ" : "لح",
        "ﱁ" : "لخ",
        "ﳋ" : "لخ",
        "ﱂ" : "لم",
        "ﲅ" : "لم",
        "ﳌ" : "لم",
        "ﳭ" : "لم",
        "ﱃ" : "لى",
        "ﲆ" : "لى",
        "ﱄ" : "لي",
        "ﲇ" : "لي",
        "ﱅ" : "مج",
        "ﳎ" : "مج",
        "ﱆ" : "مح",
        "ﳏ" : "مح",
        "ﱇ" : "مخ",
        "ﳐ" : "مخ",
        "ﱈ" : "مم",
        "ﲉ" : "مم",
        "ﳑ" : "مم",
        "ﱉ" : "مى",
        "ﱊ" : "مي",
        "ﱋ" : "نج",
        "ﳒ" : "نج",
        "ﱌ" : "نح",
        "ﳓ" : "نح",
        "ﱍ" : "نخ",
        "ﳔ" : "نخ",
        "ﱎ" : "نم",
        "ﲌ" : "نم",
        "ﳕ" : "نم",
        "ﳮ" : "نم",
        "ﱏ" : "نى",
        "ﲎ" : "نى",
        "ﱐ" : "ني",
        "ﲏ" : "ني",
        "ﱑ" : "هج",
        "ﳗ" : "هج",
        "ﱒ" : "هم",
        "ﳘ" : "هم",
        "ﱓ" : "هى",
        "ﱔ" : "هي",
        "ﱕ" : "يج",
        "ﳚ" : "يج",
        "ﱖ" : "يح",
        "ﳛ" : "يح",
        "ﱗ" : "يخ",
        "ﳜ" : "يخ",
        "ﱘ" : "يم",
        "ﲓ" : "يم",
        "ﳝ" : "يم",
        "ﳰ" : "يم",
        "ﱙ" : "يى",
        "ﲕ" : "يى",
        "ﱚ" : "يي",
        "ﲖ" : "يي",
        "ﱛ" : "ذ",
        "ﱜ" : "ر",
        "ﱝ" : "ى",
        "ﲐ" : "ى",
        "ﱤ" : "ئر",
        "ﱥ" : "ئز",
        "ﱧ" : "ئن",
        "ﱪ" : "بر",
        "ﱫ" : "بز",
        "ﱭ" : "بن",
        "ﱰ" : "تر",
        "ﱱ" : "تز",
        "ﱳ" : "تن",
        "ﱶ" : "ثر",
        "ﱷ" : "ثز",
        "ﱹ" : "ثن",
        "ﲈ" : "ما",
        "ﲊ" : "نر",
        "ﲋ" : "نز",
        "ﲍ" : "نن",
        "ﲑ" : "ير",
        "ﲒ" : "يز",
        "ﲔ" : "ين",
        "ﲙ" : "ئخ",
        "ﲛ" : "ئه",
        "ﳠ" : "ئه",
        "ﲠ" : "به",
        "ﳢ" : "به",
        "ﲥ" : "ته",
        "ﳤ" : "ته",
        "ﲲ" : "صخ",
        "ﳍ" : "له",
        "ﳖ" : "نه",
        "ﳯ" : "نه",
        "ﳙ" : "ه",
        "ﳞ" : "يه",
        "ﳱ" : "يه",
        "ﳦ" : "ثه",
        "ﳨ" : "سه",
        "ﴱ" : "سه",
        "ﳩ" : "شم",
        "ﴌ" : "شم",
        "ﴨ" : "شم",
        "ﴰ" : "شم",
        "ﳪ" : "شه",
        "ﴲ" : "شه",
        "ﳵ" : "طى",
        "ﴑ" : "طى",
        "ﳶ" : "طي",
        "ﴒ" : "طي",
        "ﳷ" : "عى",
        "ﴓ" : "عى",
        "ﳸ" : "عي",
        "ﴔ" : "عي",
        "ﳹ" : "غى",
        "ﴕ" : "غى",
        "ﳺ" : "غي",
        "ﴖ" : "غي",
        "ﳻ" : "سى",
        "ﴗ" : "سى",
        "ﳼ" : "سي",
        "ﴘ" : "سي",
        "ﳽ" : "شى",
        "ﴙ" : "شى",
        "ﳾ" : "شي",
        "ﴚ" : "شي",
        "ﳿ" : "حى",
        "ﴛ" : "حى",
        "ﴀ" : "حي",
        "ﴜ" : "حي",
        "ﴁ" : "جى",
        "ﴝ" : "جى",
        "ﴂ" : "جي",
        "ﴞ" : "جي",
        "ﴃ" : "خى",
        "ﴟ" : "خى",
        "ﴄ" : "خي",
        "ﴠ" : "خي",
        "ﴅ" : "صى",
        "ﴡ" : "صى",
        "ﴆ" : "صي",
        "ﴢ" : "صي",
        "ﴇ" : "ضى",
        "ﴣ" : "ضى",
        "ﴈ" : "ضي",
        "ﴤ" : "ضي",
        "ﴉ" : "شج",
        "ﴥ" : "شج",
        "ﴭ" : "شج",
        "ﴷ" : "شج",
        "ﴊ" : "شح",
        "ﴦ" : "شح",
        "ﴮ" : "شح",
        "ﴸ" : "شح",
        "ﴋ" : "شخ",
        "ﴧ" : "شخ",
        "ﴯ" : "شخ",
        "ﴹ" : "شخ",
        "ﴍ" : "شر",
        "ﴩ" : "شر",
        "ﴎ" : "سر",
        "ﴪ" : "سر",
        "ﴏ" : "صر",
        "ﴫ" : "صر",
        "ﴐ" : "ضر",
        "ﴬ" : "ضر",
        "ﵐ" : "تجم",
        "ﵑ" : "تحج",
        "ﵒ" : "تحج",
        "ﵓ" : "تحم",
        "ﵔ" : "تخم",
        "ﵕ" : "تمج",
        "ﵖ" : "تمح",
        "ﵗ" : "تمخ",
        "ﵘ" : "جمح",
        "ﵙ" : "جمح",
        "ﵚ" : "حمي",
        "ﵛ" : "حمى",
        "ﵜ" : "سحج",
        "ﵝ" : "سجح",
        "ﵞ" : "سجى",
        "ﵟ" : "سمح",
        "ﵠ" : "سمح",
        "ﵡ" : "سمج",
        "ﵢ" : "سمم",
        "ﵣ" : "سمم",
        "ﵤ" : "صحح",
        "ﵥ" : "صحح",
        "ﵦ" : "صمم",
        "ﷅ" : "صمم",
        "ﵧ" : "شحم",
        "ﵨ" : "شحم",
        "ﵩ" : "شجي",
        "ﵪ" : "شمخ",
        "ﵫ" : "شمخ",
        "ﵬ" : "شمم",
        "ﵭ" : "شمم",
        "ﵮ" : "ضحى",
        "ﵯ" : "ضخم",
        "ﵰ" : "ضخم",
        "ﵱ" : "طمح",
        "ﵲ" : "طمح",
        "ﵳ" : "طمم",
        "ﵴ" : "طمي",
        "ﵵ" : "عجم",
        "ﷄ" : "عجم",
        "ﵶ" : "عمم",
        "ﵷ" : "عمم",
        "ﵸ" : "عمى",
        "ﵹ" : "غمم",
        "ﵺ" : "غمي",
        "ﵻ" : "غمى",
        "ﵼ" : "فخم",
        "ﵽ" : "فخم",
        "ﵾ" : "قمح",
        "ﶴ" : "قمح",
        "ﵿ" : "قمم",
        "ﶀ" : "لحم",
        "ﶵ" : "لحم",
        "ﶁ" : "لحي",
        "ﶂ" : "لحى",
        "ﶃ" : "لجج",
        "ﶄ" : "لجج",
        "ﶅ" : "لخم",
        "ﶆ" : "لخم",
        "ﶇ" : "لمح",
        "ﶈ" : "لمح",
        "ﶉ" : "محج",
        "ﶊ" : "محم",
        "ﶋ" : "محي",
        "ﶌ" : "مجح",
        "ﶍ" : "مجم",
        "ﶎ" : "مخج",
        "ﶏ" : "مخم",
        "ﶒ" : "مجخ",
        "ﶓ" : "همج",
        "ﶔ" : "همم",
        "ﶕ" : "نحم",
        "ﶖ" : "نحى",
        "ﶗ" : "نجم",
        "ﶘ" : "نجم",
        "ﶙ" : "نجى",
        "ﶚ" : "نمي",
        "ﶛ" : "نمى",
        "ﶜ" : "يمم",
        "ﶝ" : "يمم",
        "ﶞ" : "بخي",
        "ﶟ" : "تجي",
        "ﶠ" : "تجى",
        "ﶡ" : "تخي",
        "ﶢ" : "تخى",
        "ﶣ" : "تمي",
        "ﶤ" : "تمى",
        "ﶥ" : "جمي",
        "ﶦ" : "جحى",
        "ﶧ" : "جمى",
        "ﶨ" : "سخى",
        "ﶩ" : "صحي",
        "ﶪ" : "شحي",
        "ﶫ" : "ضحي",
        "ﶬ" : "لجي",
        "ﶭ" : "لمي",
        "ﶮ" : "يحي",
        "ﶯ" : "يجي",
        "ﶰ" : "يمي",
        "ﶱ" : "ممي",
        "ﶲ" : "قمي",
        "ﶳ" : "نحي",
        "ﶶ" : "عمي",
        "ﶷ" : "كمي",
        "ﶸ" : "نجح",
        "ﶽ" : "نجح",
        "ﶹ" : "مخي",
        "ﶺ" : "لجم",
        "ﶼ" : "لجم",
        "ﶻ" : "كمم",
        "ﷃ" : "كمم",
        "ﶾ" : "جحي",
        "ﶿ" : "حجي",
        "ﷀ" : "مجي",
        "ﷁ" : "فمي",
        "ﷂ" : "بحي",
        "ﷆ" : "سخي",
        "ﷇ" : "نجي",
        "ﻵ" : "لآ",
        "ﻶ" : "لآ",
        "ﻷ" : "لأ",
        "ﻸ" : "لأ",
        "ﻹ" : "لإ",
        "ﻺ" : "لإ",
        "ﻻ" : "لا",
        "ﻼ" : "لا",
        "ﷺ" : "صلى الله عليه وسلم",
        "﷽" : "بسم الله الرحمن الرحيم",
        "ﷲ" : "الله",
        "ﷳ" : "أكبر",
        "ﷴ" : "محمد",
        "ﷶ" : "رسول",
        "ﷷ" : "عليه",
        "ﷸ" : "وسلم",
        "ﷹ" : "صلى",
        "﷼" : "ریال",
        "ﷻ" : "جل جلاله",
        "ﷱ" : "قلے",
        "ﷰ" : "صلے",
        "ﷵ" : "صلعم",
    }

    PALEO_MAPPING = {
        'ء' : 'ʔ' ,
        'أ' : 'اˀ' ,
        'ﺃ' : 'اˀ' ,
        'ﺄ' : 'اˀ' ,
        'ٲ' : 'اˀ' ,
        'ٵ' : 'اˀ' ,
        'إ' : 'اɂ' ,
        'ﺇ' : 'اɂ' ,
        'ﺈ' : 'اɂ' ,
        'ٳ' : 'اɂ' ,
        'ٱ' : 'اᵟ' ,
        'ﭐ' : 'اᵟ' ,
        'ﭑ' : 'اᵟ' ,
        'آ' : 'ا˜' ,
        'آ' : 'ا˜' ,
        'ﺁ' : 'ا˜' ,
        'ﺂ' : 'ا˜' ,
        'ﴼ' : 'اᵃⁿ',
        'ݳ' : 'ا۲',  # Urdu/Persian encoding of Numerals
        'ݴ' : 'ا۳',
        'ࢥ' : 'ٯ₁' , # U+08a5 ARABIC LETTER QAF WITH DOT BELOW
        'ڧ' : 'ٯ¹' ,
        'ق' : 'ٯ²' ,
        'ڨ' : 'ٯ³' ,
        'ﻕ' : 'ٯ²' ,
        'ﻖ' : 'ٯ²' ,
        'ن' : 'ں¹' ,
        'ڹ' : 'ں₁' ,
        'ݧ' : 'ں₂' ,
        'ڽ' : 'ں³' ,
        'ﻥ' : 'ں¹' ,
        'ﻦ' : 'ں¹' ,
        'ڻ' : 'ںᵀ' ,
        'ڼ' : 'ںₒ' ,
        'ݨ' : 'ںᵀ¹' ,  # we encode from up to bottom
        'ݩ' : 'ںᵛ¹' ,
        'ي' : 'ی₂' ,  # U+064a Arabic ya (normalise to Persian ya)
        #'ی' : 'ی' ,   # U+06cc Farsi ya
        'ى' : 'ی' ,   # U+0649 Alif maqsura (normalise to Persian ya)
        'ې' : 'ی₂' ,
        'ۑ' : 'ی₃' ,
        'ؾ' : 'ی²' ,
        'ؿ' : 'ی³' ,
        'ﻲ' : 'ی₂' ,
        'ﮰ' : 'یˀ' ,
        'ﮱ' : 'یˀ' ,
        'ﺉ' : 'یˀ' ,
        'ﺊ' : 'یˀ' ,
        'ئ' : 'یˀ' ,
        'ۓ' : 'یˀ' ,
        'ݷ' : 'ی۴' ,
        'ؠ' : 'یₒ' ,
        'ؽ' : 'یᶺ' ,
        'ێ' : 'یᵛ' ,
        'ݵ' : 'ی۲' ,
        'ݶ' : 'ی۳' ,
        'ݺ' : 'ی۲' ,
        'ݻ' : 'ی۳' ,
        'ب' : 'ٮ₁' ,
        'ٻ' : 'ٮ₂' ,
        'ݐ' : 'ٮ₃' ,
        'پ' : 'ٮ₃' ,
        'ڀ' : 'ٮ₄' ,
        'ݒ' : 'ٮ₃' ,
        'ݔ' : 'ٮ¹₂' ,
        'ت' : 'ٮ²' ,   # we don't keep a distinction between this and the next
        'ٺ' : 'ٮ²' ,   # (there are other cases like this one)
        'ݓ' : 'ٮ²₃' ,
        'ث' : 'ٮ³' ,
        'ٽ' : 'ٮ³' ,
        'ٿ' : 'ٮ⁴' ,
        'ݑ' : 'ٮ³₁' ,
        'ﻧ' : 'ٮ¹' ,
        'ﻨ' : 'ٮ¹' ,
        'ﯾ' : 'ٮ₂' ,
        'ﯿ' : 'ٮ₂' ,
        'ﻳ' : 'ٮ₂' ,
        'ﻴ' : 'ٮ₂' ,
        'ﺋ' : 'ٮˀ' ,
        'ﺌ' : 'ٮˀ' ,
        'ﺏ' : 'ٮ₁' ,
        'ﺐ' : 'ٮ₁' ,
        'ﺑ' : 'ٮ₁' ,
        'ﺒ' : 'ٮ₁' ,
        'ﭖ' : 'ٮ₃' ,
        'ﭗ' : 'ٮ₃' ,
        'ﭘ' : 'ٮ₃' ,
        'ﭙ' : 'ٮ₃' ,
        'ﺕ' : 'ٮ²' ,
        'ﺖ' : 'ٮ²' ,
        'ﺗ' : 'ٮ²' ,
        'ﺘ' : 'ٮ²' ,
        'ﺙ' : 'ٮ³' ,
        'ﺚ' : 'ٮ³' ,
        'ﺛ' : 'ٮ³' ,
        'ﺜ' : 'ٮ³' ,
        'ࢬ' : 'ٮ₂' ,
        'ݕ' : 'ٮ‸' ,
        'ࢠ' : 'ٮᵥ' ,
        'ٹ' : 'ٮᵀ' ,
        'ݖ' : 'ٮᵛ' ,
        'ټ' : 'ٮₒ' ,
        'خ' : 'ح¹' ,
        'ج' : 'ح₁' ,
        'چ' : 'ح₃' ,
        'ڃ' : 'ح₂' ,
        'ڄ' : 'ح₂' ,
        'چ' : 'ح₃' ,
        'ڇ' : 'ح₄' ,
        'ݘ' : 'ح₃' ,
        'ڿ' : 'ح¹₃' ,
        'ڂ' : 'ح²' ,
        'ݗ' : 'ح²' ,
        'ࢢ' : 'ح₂' ,  # U+08a2 ARABIC LETTER JEEM WITH TWO DOTS ABOVE
        'څ' : 'ح³' ,
        'ﺝ' : 'ح₁' ,
        'ﺞ' : 'ح₁' ,
        'ﺟ' : 'ح₁' ,
        'ﺠ' : 'ح₁' ,
        'ﺥ' : 'ح¹' ,
        'ﺦ' : 'ح¹' ,
        'ﺧ' : 'ح¹' ,
        'ﺨ' : 'ح¹' ,
        'ﭺ' : 'ح₃' ,
        'ﭻ' : 'ح₃' ,
        'ﭼ' : 'ح₃' ,
        'ﭽ' : 'ح₃' ,
        'ځ' : 'حˀ' ,
        'ݮ' : 'حт' ,
        'ݼ' : 'ح۴' ,
        'ݯ' : 'حт₂' ,
        'ݲ' : 'حᵀ' ,
        'ز' : 'ر¹' ,
        'ڔ' : 'ر₁' ,
        'ݬ' : 'رˀ' ,
        'ږ' : 'ر¹₁' ,
        'ڗ' : 'ر²' ,
        'ݫ' : 'ر²' ,
        'ژ' : 'ر³' ,
        'ڙ' : 'ر⁴' ,
        'ﺯ' : 'ر¹' ,
        'ﺰ' : 'ر¹' ,
        'ﮊ' : 'ر³' ,
        'ﮋ' : 'ر³' ,
        'ړ' : 'رₒ' ,
        'ݛ' : 'ر₋' ,
        'ࢪ': 'ر' , # U+08aa ARABIC LETTER REH WITH LOOP
        'ڕ' : 'رᵥ' ,
        'ڑ' : 'رᵀ' ,
        'ڒ' : 'رᵛ' ,
        'ۯ' : 'رᶺ' ,
        'ݱ' : 'رᵀ²' ,
        'ذ' : 'د¹' ,
        'ڊ' : 'د₁' ,
        'ڍ' : 'د₂' ,
        'ڌ' : 'د²' ,
        'ڎ' : 'د³' ,
        'ڏ' : 'د³' ,
        'ڐ' : 'د⁴' ,
        'ﺫ' : 'د¹' ,
        'ﺬ' : 'د¹' ,
        'ڈ' : 'دᵀ' ,
        'ډ' : 'دₒ' ,
        'ݚ' : 'د‸' ,
        'ۮ' : 'دᶺ' ,
        'ڋ' : 'دᵀ₁' ,
        'ݙ' : 'دᵀ₂' ,
        'ظ' : 'ط¹' ,
        'ࢣ' : 'ط²' ,  # U+08a3 ARABIC LETTER TAH WITH TWO DOTS ABOVE
        'ڟ' : 'ط³' ,
        'ﻅ' : 'ط¹' ,
        'ﻆ' : 'ط¹' ,
        'ﻇ' : 'ط¹' ,
        'ﻈ' : 'ط¹' ,
        'ض' : 'ص¹' ,
        'ڝ' : 'ص₂' ,
        'ۻ' : 'ص¹₁' ,
        'ڞ' : 'ص³' ,
        'ﺽ' : 'ص¹' ,
        'ﺾ' : 'ص¹' ,
        'ﺿ' : 'ص¹' ,
        'ﻀ' : 'ص¹' ,
        'ش' : 'س³' ,
        'ڛ' : 'س₃' ,
        'ښ' : 'س¹₁' ,
        'ݭ' : 'س²' ,
        'ݜ' : 'س³' ,
        'ۺ' : 'س³₁' ,
        'ڜ' : 'س³₃' ,
        'ﺵ' : 'س³' ,
        'ﺶ' : 'س³' ,
        'ﺷ' : 'س³' ,
        'ﺸ' : 'س³' ,
        'ݽ' : 'س۴' ,
        'ݾ' : 'سᶺ' ,
        'ݰ' : 'سᵀ²' ,
        'ف' : 'ڡ¹' ,
        'ﻑ' : 'ڡ¹' ,
        'ﻒ' : 'ڡ¹' ,
        'ڢ' : 'ڡ₁' ,
        'ݠ' : 'ڡ₂' ,
        'ڥ' : 'ڡ₃' ,
        'ݡ' : 'ڡ₃' ,
        'ڣ' : 'ڡ¹₁' ,
        'ڤ' : 'ڡ³' ,
        'ڦ' : 'ڡ⁴' ,
        'ࢤ' : 'ڡ³₁' ,  # U+08a4 ARABIC LETTER FEH WITH DOT BELOW AND THREE DOTS ABOVE
        'ﻓ' : 'ڡ¹' ,
        'ﻔ' : 'ڡ¹' ,
        'ﻗ' : 'ڡ²' ,
        'ﻘ' : 'ڡ²' ,
        'غ' : 'ع¹' ,
        'ۼ' : 'ع¹₁' ,
        'ݝ' : 'ع²' ,
        'ݟ' : 'ع²' ,
        'ڠ' : 'ع³' ,
        'ݞ' : 'ع³' ,
        'ﻍ' : 'ع¹' ,
        'ﻎ' : 'ع¹' ,
        'ﻏ' : 'ع¹' ,
        'ﻐ' : 'ع¹' ,
        'ؤ' : 'وˀ' ,
        'ۏ' : 'و¹' ,
        'ۊ' : 'و²' ,
        'ۋ' : 'و³' ,
        'ﺅ' : 'وˀ' ,
        'ﺆ' : 'وˀ' ,
        'ۄ' : 'وₒ' , #FIXME
        'ۅ' : 'و₋' , #FIXME
        'ࢫ' : 'وₒ' , # U+08ab ARABIC LETTER WAW WITH DOT WITHIN #FIXME
        'ۆ' : 'وᵛ' ,
        'ۇ' : 'وᵠ' ,  #FIXME
        'ۈ' : 'و।' ,  #FIXME
        'ۉ' : 'وᶺ' ,
        'ݸ' : 'و۲' ,
        'ݹ' : 'و۳' ,
        'ۀ' : 'هˀ' ,
        'ۂ' : 'هˀ' ,
        'ة' : 'ه²' ,
        'ۃ' : 'ه²' ,
        'ﮤ' : 'هˀ' ,
        'ﮥ' : 'هˀ' ,
        'ﺓ' : 'ه²' ,
        'ﺔ' : 'ه²' ,
        'ۿ' : 'هᶺ' ,
        'ݦ' : 'م₁' ,
        'ݥ' : 'م¹' ,
        'ࢧ' : 'م³' ,  # U+08a7 ARABIC LETTER MEEM WITH THREE DOTS ABOVE
        'ڸ' : 'ل₃' ,
        'ڶ' : 'ل¹' ,
        'ڷ' : 'ل³' ,
        'ݪ' : 'ل₋' ,
        'ڵ' : 'لᵛ' ,
        'ؼ' : 'ك₃' ,
        'ڮ' : 'ك₃' ,
        'ݤ' : 'ك₃' ,
        'ݢ' : 'ك¹' ,
        'ػ' : 'ك²' ,
        'ݿ' : 'ك²ˀ' ,
        'ڭ' : 'ك³' ,
        'ݣ' : 'ك³' ,
        'ګ' : 'ك' ,  # FIXME
        'ڰ' : 'كᐟ' ,  #FIXME
        'ڲ' : 'كᐟ₂' ,
        'ڳ' : 'كᐟ₂' ,
        'ڱ' : 'ك²ᐟ' ,
        'ڴ' : 'ك³ᐟ' ,
        'گ' : 'كᐟ' ,
        'ﮓ' : 'كᐟ' ,
        'ﮔ' : 'كᐟ' ,
        'ﮕ' : 'كᐟ' ,
        'َ' : 'ᵃ'  ,  # fatha
        'ً' : 'ᵃⁿ' ,  # fathatan
        'ࣰ' : 'ᵃᵃ' ,  # open fathatan
        'ُ' : 'ᵘ'  ,  # damma
        'ٌ' : 'ᵘⁿ' ,   # dammatan
        'ࣱ' : 'ᵘᵘ' ,  # open dammatan
        'ِ' : 'ᵢ'  ,  # kasra
        'ٍ' : 'ᵢₙ' ,  # kasratan
        'ࣲ' : 'ᵢᵢ' ,  # open kasratan
        'ّ' : 'ᵚ'  ,  # sadda
        'ۡ' : 'ᵒ'  ,  # quranic sukun
        'ْ' : 'ᵒ'  ,  # normal sukun
        'ٓ' : '˜'  ,  # madda
        'ۨ' : 'ᴺ'  ,  # minuature nun above
        'ٰ' : 'ᴬ'  ,  # dagger alif
        'ۜ' : 'ˢ'  ,  # miniature sin above
        'ۣ' : 'ₛ'  ,  # miniature sin below
        'ۢ' : 'ᵐ'  ,  # minuature mim above   #FIXME Mᴹᴍ Yyʏ
        'ۭ' : 'ₘ' ,  # # minuature mim below
        'ۥ' : 'ʷ'  ,  # minuature waw
        'ۦ' : 'ʸ'  ,  # miniature ya
        'ۧ' : 'ʸ'  ,  # minuature ya above
        '۟' : '°'  ,  # U+06df ARABIC SMALL HIGH ROUNDED ZERO - small circle | U+00B0 DEGREE SIGN
                      #   the letter is additional and should not be pronounced either in connection nor pause
        '۠' : '⁰'  ,  # U+06e0 ARABIC SMALL HIGH UPRIGHT RECTANGULAR ZERO - oval sign
                      #   above an alif followed by a vowel letter, indicates that it is additional in consecutive reading
                      #   but should be pronounced in pause
        '۫' : '⌃'  ,  # U+06eb ARABIC EMPTY CENTRE HIGH STOP | U+2303 (alt-08963)  UP ARROWHEAD ; hapax تَأۡمَ۫نَّا
        '۪' : '⌄'  ,  # U+06ea ARABIC EMPTY CENTRE LOW STOP | U+2304 DOWN ARROWHEAD ; hapax مَجۡر۪ىٰهَا
        '۬' : '•'  ,  # U+06ec ARABIC ROUNDED HIGH STOP WITH FILLED CENTRE | U+2022 BULLET ; hapax ءَا۬عۡجَمِىࣱّ
        'ٔ' : 'ˀ' ,  # hamza above
        'ٕ' : 'ɂ'  ,  # hamza below
        #'ـٔ ' : 'ˀ' ,  # U+0640 "ـ" tatweel is ALWAYS followed by hamza above, eg. ٱلۡأَفۡـِٔدَةِ 104:7:4,601:49,821:8:4
        # pausal marks
        'ۖ' : '⒮',  # U+06d6 ARABIC SMALL HIGH LIGATURE SAD WITH LAM WITH ALEF MAKSURA
        'ۗ' : '⒬',  # U+06d7 ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA
        'ۘ' : '⒨',  # U+06d8 ARABIC SMALL HIGH MEEM INITIAL FORM
        'ۙ' : '⒧',  # U+06d9 ARABIC SMALL HIGH LAM ALEF
        'ۚ' : '⒥',  # U+06da ARABIC SMALL HIGH JEEM
        'ۛ' : '∴',   # U+06db ARABIC SMALL HIGH THREE DOTS
    }

    CLUSTERS_REGEX = re.compile('|'.join(CLUSTERS))
    CLEAN_REGEX = re.compile(fr'[^{CHAR}]')

    RASM_QNY_REGEX = re.compile(fr'({"|".join(RASM_QNY_MAPPING)})$')
    RASM_REGEX = re.compile(fr'[{"".join(RASM_MAPPING)}]')
    ABJAD_REGEX = re.compile('|'.join(ABJAD_MAPPING))

    PALEO_REGEX = re.compile('|'.join(PALEO_MAPPING))
    PALEO_N_REGEX = re.compile(fr'[ںنڻڼڹݧݨݩڽﻥﻦ](?=[^{CHAR}]*$)')
    PALEO_Q_REGEX = re.compile(fr'[ٯࢥڧقڨﻕﻖ](?=[^{CHAR}N]*$)')
    PALEO_Y_REGEX = re.compile(fr'[ىیۍݷيېۑؠئؽێݵݶࢨࢩؾؿےۓݺݻﻯﻰﮮﮯﯼﯽﻲﮰﮱﺉﺊ](?=[^{CHAR}NQ]*$)')

    CREAN_RASM_REGEX = re.compile(r'[^A-Y ]')

    # separate blocks in archigraphemic representation
    ARDW_REGEX = re.compile(r'([ARDW][^QNYABGRDTCSFEWHMLK]*)')

    # separate blocks in arabic graphemic representation
    ARDW_AR = ''.join((A, R, D, W))
    BLOCKS_REGEX = re.compile(rf'((?:[{ARDW_AR}]|.+?[{ARDW_AR}])[^{CHAR}]*|.+)')

    UNSTABLE_ALIF_REGEX = re.compile(r'ᵃA(?=.)')
    UNSTABLE_ALIF_ARA_REGEX = re.compile(r'َا(?=.)')

def _to_paleo(tokens, /, unstable_alif=False):
    """ Convert Arabic-scriped token into paleo-orthographic representation and create copy in rasm representation.

    Args:
        tokens (iterator): stream to convert.
        unstable_alif (bool): if True, delete fatha+alif in conversion.

    Yield:
        str, str, str: original token, token in paleo-prthographic representation,rasmired token in Latin, rasmired token in Arabic.

    """
    for tok in tokens:
        pal = tok

        # convert to paleo general
        pal = DATA.PALEO_REGEX.sub(lambda m: DATA.PALEO_MAPPING[m.group(0)], pal)

        # restore consonantal diacritics for ya when appropriate
        pal = re.sub(f'[یى](?=[^ا-ی]*[ا-ی])(?!₂|ɂ|ˀ|ᴬ)', 'ی₂', pal)

        # convert to paleo NQY
        pal = DATA.PALEO_N_REGEX.sub('N', pal)
        pal = DATA.PALEO_Q_REGEX.sub('Q', pal)
        pal = DATA.PALEO_Y_REGEX.sub('Y', pal)

        # convert graphemes to rasm
        pal = DATA.RASM_REGEX.sub(lambda m: DATA.RASM_MAPPING[m.group(0)], pal)
        if unstable_alif:
            pal = DATA.UNSTABLE_ALIF_REGEX.sub('', pal)

        pal = DATA.ARDW_REGEX.sub(r'\1 ', pal)

        # make copy with only archigraphemes
        rlt = DATA.CREAN_RASM_REGEX.sub('', pal)

        rar = DATA.ABJAD_REGEX.sub(lambda m: ABJAD_MAPPING[m.group(0)], rlt)

        yield tok, rlt, rar, pal

def _tokenise(stream, /, norm_clusters=False):
    """ Segment stream in tokens.

    Args:
        stream (iterator): text to split.
        norm_clusters (bool): normalise clusters before tokenising.

    Yield:
        str: splitted token.

    """
    if norm_clusters:
        stream = (DATA.CLUSTERS_REGEX.sub(lambda m: DATA.CLUSTERS[m.group(0)], line) for line in stream)

    yield from (tok for line in stream for tok in re.split(rf'[{whitespace}{punctuation}؟،؛]', line) if tok)

def _clean(tokens, /, unstable_alif=False):
    """ Create a copy each token in tokens containing no Arabic-scripted characters.

    Args:
        tokens (iterator): tokens to clean.
        unstable_alif (bool): if True, delete fatha+alif in conversion.

    Yield:
        str, str: original token, cleaned token. Nothing if clean token is empty.

    """
    if unstable_alif:
        tokens = (DATA.UNSTABLE_ALIF_ARA_REGEX.sub('', tok) for tok in tokens)
    yield from ((ori, DATA.CLEAN_REGEX.sub('', ori)) for ori in tokens)

def _to_rasm(tokens):
    """ Convert cleantok to archigraphemic representation.

    Args:
        tokens (iterator): stream to convert.

    Yield:
        str, str, str: original token, rasmired token in Latin, rasmired token in Arabic.

    """
    tokens_qny = ((ori, DATA.RASM_QNY_REGEX.sub(lambda m: DATA.RASM_QNY_MAPPING[m.group(0)], clean)) for ori, clean in tokens)

    tokens_rasm = ((ori, DATA.RASM_REGEX.sub(lambda m: DATA.RASM_MAPPING[m.group(0)], rasm)) for ori, rasm in tokens_qny)

    tokens_rblocks = ((ori, re.sub(r'([ARDW])', r'\1 ', rasm)) for ori, rasm in tokens_rasm)

    yield from ((ori, rasm, DATA.ABJAD_REGEX.sub(lambda m: ABJAD_MAPPING[m.group(0)], rasm)) for ori, rasm in tokens_rblocks)

def _uniq(stream, /, paleo=False):
    """ Map each rasm block with the list of blocks or tokens they appear in
    and calculate number of occurrences.

    Args:
        stream (iterator): sequence of Arabic token, rasm in Latin script, rasm in Arabic script and
            paleo-orthphraphic representation (optional).
        paleo (bool): includes paleo-orthographic representation.

    Yield:
        str, int, set: block in Latin script, block in Arabic script, number of occurrences, tokens where
            block appears or 2-item tuples containing ori token and paleo-orthographic representation.

    """
    if paleo:
        blocks = sorted(((*bl, pal, ori) for ori, *rsm, pal in stream for bl in zip(*(c.split() for c in rsm))), key=lambda x: x[0])
        groups = ((k, [(ori, pal) for *_, pal, ori in gr]) for k, gr in groupby(blocks, key=lambda x : (x[:2])))

    else:
        blocks = sorted(((*bl, ori) for ori, *rsm in stream for bl in zip(*(c.split() for c in rsm))), key=lambda x: x[0])
        groups = ((k, [ori for *_, ori in gr]) for k, gr in groupby(blocks, key=lambda x : (x[:2])))

    yield from sorted(((*block, len(gr), set(gr)) for block, gr in groups), key=lambda x: x[2], reverse=True)

def _get_blocks(index, source='tanzil-simple', only_rasm=False):
    """ Get sequence of Quran blocks from Quran index range.

    Args:
        index (tuple): Quran index range of text to retrieve as archigraphemes.
            Format of the index: ((i, j, k, m), (n, p, q, r)). All integers can be None except i.
        source ("tanzil-simple", "tanzil-uthmani", "decotype"): indicate the text source from which to retrieve the results.
            If the source is different from the three indicated above, tanzil-simple will be used.
        only_rasm (bool): do not print start of rub el hizb (۞ U+06de) nor place of sajda (۩ U+06e9) in output.
        unstable_alif (bool): if True, delete fatha+alif in conversion.

    Yield:
        tuple: (original_token, rarm_latin, rarm_arabic, paleo), (sura_page, vers_line, word, block)

    Raise:
        IndexError: when Quran index is out of range.
        PrivateFileError: decotype file is private.

    """ 
    if source == 'tanzil-uthmani':
        source_file = SOURCE.TANZIL_UTHMANI
    elif source == 'decotype':
        source_file = SOURCE.DECOTYPE
    else:
        source_file = SOURCE.TANZIL_SIMPLE

    source_path = files('rasm_arch_data').joinpath(source_file)

    if source == 'decotype' and not source_path.exists():
        raise PrivateFileError

    with source_path.open() as fp:
        quran = json.load(fp)
    
        i, j, k, m = [(ind-1 if ind else ind) for ind in index[0]]
        n, p, q, r = [(ind-1 if ind else ind) for ind in index[1]]

        # we put a maximum upper limit in the end index, copying the start index when the end is absent
        if (n, p, q, r) == (None, None, None, None):
            n, p, q, r = i, j, k, m

        for isura in range(i, len(quran['ind'])):
    
            if n != None:
                if isura > n:
                    return
    
            else:
                if isura > i:
                    return
    
            for ivers in range(len(quran['ind'][isura])):
    
                if j != None and isura == i and ivers < j:
                    continue
    
                if p != None and isura == n and ivers > p:
                    return
    
                for iword in range(len(quran['ind'][isura][ivers])):
    
                    if k != None and isura == i and ivers == j and iword < k:
                        continue
    
                    if q != None and isura == n and ivers == p and iword > q:
                        return
    
                    for iblock in range(len(quran['ind'][isura][ivers][iword])):
                        if m != None and isura == i and ivers == j and iword == k and iblock < m:
                            continue
    
                        if r != None and isura == n and ivers == p and iword == q and iblock > r:
                            return
    
                        block = quran['ind'][isura][ivers][iword][iblock]

                        tok, pal = quran['tok'][block]
                        rlt = DATA.CREAN_RASM_REGEX.sub('', pal)
                        rar = DATA.ABJAD_REGEX.sub(lambda m: ABJAD_MAPPING[m.group(0)], rlt)

                        if not only_rasm or tok not in ('۞', '۩'):
                            yield (tok, rlt, rar, pal), (isura+1, ivers+1, iword+1, iblock+1)


@singledispatch
def rasm_arch(input_):
    raise NotImplementedError('Unsupported type')

@rasm_arch.register(TextIOBase)
def _(input_, /, paleo=False, blocks=False, uniq=False, norm_clusters=False, unstable_alif=False):
    """ Clean, tokenise and convert text to archigraphemic representation.

               +----------------+     +-----------+     +--------+     +----------+     
     input --> | _norm_clusters | --> | _tokenise | --> | _clean | --> | _to_rasm | ----+---> output 
            |  +----------------+     +-----------+     +--------+     +----------+     | 
            |                              |                                |    +------+
            +------------------------------+                                +--> | uniq |
                                           |                                     +------+
                                           |                      +-----------+      |
                                           +--------------------> | _to_paleo | -----+
                                                                  +-----------+

    Args:
        input_ (io.TextIOBase): text to convert to archigraphemes, e.g.
            
            "كبيكج وكيتكج والجِنّ"

        paleo (bool): convert to paleo-orthographic representation instead of bare rasm.
        blocks (bool): yield results in letterblocks, not words (irrelevant if uniq == True).
        uniq (bool): if True, map letterblocks with list of tokens the appear and show absolute frequency.
        norm_clusters (bool): if True, normalise Arabic clusters to decomposed form before conversion.
        unstable_alif (bool): if True, delete fatha+alif in conversion.

    Yield:
        (if uniq==False and blocks==False and paleo==False)
        str, str, str: original word, rasmised word in Latin, rasmised word in Arabic, e.g.

            ("كبيكج", "KBBKG", "کٮٮکح")
            ("وكيتكج", "WKBBKG", "وکٮٮکح")
            ("والجِنّ", "WALGN", "والحں")

    Yield:
        (if uniq==False and blocks==False and paleo==True)
        str, str, str, str: original word, rasmised word in Latin, rasmised word in Arabic, paleo-orthographic representaiton of word, e.g.

            ("كبيكج", "KBBKG", "كٮٮكح", "KB₁B₂KG₁")
            ("وكيتكج", "WKBBKG", "وكٮٮكح", "WKB₂B²KG₁")
            ("والجِنّ", "WALGN", "والحں", "WALG₁ᵢN¹ᵚ")

    Yield:
        (if uniq==False and blocks==True and paleo==False)
        str, list: original word, list of 2-item sets of block in Latin and block in Arabic, e.g.

            ("كبيكج", [("كبيكج", "KBBKG", "کٮٮکح")])
            ("وكيتكج", [("و", "W", "و"), ("كيتكج", "KBBKG", "کٮٮکح")])
            ("والجِنّ", [("و", "W", "و"), ("ا", "A", "ا"), ("لجِنّ", "LGN", "لحں")])

    Yield:
        (if uniq==False and blocks==True and paleo==True)
        str, list: original word, list of 3-item sets of block in Latin, block in Arabic, paleo-orthographic representaiton of block, e.g.

            ("كبيكج", [("كبيكج", "KBBKG", "كٮٮكح", "KB₁B₂KG₁")]),
            ("وكيتكج", [("و", "W", "و", "W"), ("كيتكج", "KBBKG", "كٮٮكح", "KB₂B²KG₁")]),
            ("والجِنّ", [("و", "W", "و", "W"), ("ا", "A", "ا", "A"), ("لجِنّ", "LGN", "لحں", "LG₁ᵢN¹ᵚ")])
    
    Yield:
        (if uniq==True and paleo==False ; blocks irrelevant)
        str, str, int, set: original block, rasmised block in Latin, rasmised block in Arabic, total occurrences of blocks, list of unique types where it appears, e.g.

            ("KBBKG", "کٮٮکح", 2, {"كبيكج", "وكيتكج"})
            ("W", "و", 2, {"وكيتكج", "والجِنّ"})
            ("A", "ا", 1, {"والجِنّ"})
            ("LGN", "لحں", 1, {"والجِنّ"})
    
    Yield:
        (if uniq==True and paleo==True ; blocks irrelevant)
        str, str, int, set: original block, rasmised block in Latin, rasmised block in Arabic, total occurrences of blocks, list of unique types where it appears, e.g.

            ("KBBKG", "كٮٮكح", 2, {("كبيكج", "KB₁B₂KG₁"), ("وكيتكج", "WKB₂B²KG₁")}),
            ("W", "و", 2, {("وكيتكج", "WKB₂B²KG₁"), ("والجِنّ", "WALG₁ᵢN¹ᵚ")}),
            ("A", "ا", 1, {("والجِنّ", "WALG₁ᵢN¹ᵚ")}),
            ("LGN", "لحں", 1, {("والجِنّ", "WALG₁ᵢN¹ᵚ")})

    """
    if uniq and blocks:
        blocks = False

    procs = partial(_tokenise, norm_clusters=norm_clusters),

    if paleo:
        # normalise tanwin
        input_ =  (DATA.NORM_REGEX.sub(lambda m: DATA.NORM_MAPPING[m.group(0)], s) for s in input_)
        procs += partial(_to_paleo, unstable_alif=unstable_alif),

    else:
        procs += partial(_clean, unstable_alif=unstable_alif), _to_rasm
    
    if uniq:
        procs += partial(_uniq, paleo=paleo),
    
    results = pipe(input_, *procs)
        
    if blocks:
        for ori, *rest in results:                
            yield ori, list(zip(DATA.BLOCKS_REGEX.findall(ori), *(r.split() for r in rest)))
    else:
        if uniq:
            if paleo:
                yield from ((*fst, {(word, pal.replace(' ', '')) for word, pal in found}) for *fst, found in results)
            else:
                yield from ((ori, *rest) for ori, *rest in results)
        else:
            yield from ((ori, *(r.replace(' ', '') for r in rest)) for ori, *rest in results)

@rasm_arch.register(tuple)
def _(input_, /, paleo=True, blocks=False, uniq=False, source='tanzil-simple', only_rasm=False):
    """ Retrieve quranic text in archegraphemic representation according to index range.

    Args:
        text (tuple): Quran index range of text to retrieve as archigraphemes. Format of the index:
          ((i, j, k, m), (n, p, q, r)). All integers can be None except i. E.g.

            (28, 98, 1, None), (28, 98, 8, None)

        paleo (bool): convert to paleo-orthographic representation  instead of bare rasm.
        blocks (bool): yield results in letterblocks, not words (irrelevant if uniq == True).
        uniq (bool): if True, map letterblocks with list of tokens the appear and show absolute frequency.
        source ("tanzil-simple", "tanzil-uthmani", "decotype"): indicate the text source from which to retrieve the results.
            If the source is different from the three indicated above, tanzil-simple will be used.
        unstable_alif (bool): if True, ignore alifs in rasm conversion.
        only_rasm (bool): do not print start of rub el hizb (۞ U+06de) nor place of sajda (۩ U+06e9) in output.

    Yield:
        (if uniq==False and blocks==False and paleo==False)
        str, str, str, (int, int, int): original word, rasmised word in Latin, rasmised word in Arabic, Quran index e.g.

            ("إِنَّمَآ", "ABMA", "اٮما", (20, 98, 1))
            ("إِلَٰهُكُمُ", "ALHKM", "الهکم", (20, 98, 2))
            ("ٱللَّهُ", "ALLH", "الله", (20, 98, 3))
            ("ٱلَّذِی", "ALDY", "الد ی", (20, 98, 4))
            ("لَآ", "LA", "لا", "LᵃA˜", (20, 98, 5))
            ("إِلَٰهَ", "ALH", "اله", (20, 98, 6))
            ("إِلَّا", "ALA", "الا", (20, 98, 7))
            ("هُوَۚ", "HW", "هو", "HᵘWᵃ⒥", (20, 98, 8))

    Yield:
        (if uniq==False and blocks==False and paleo==True)
        str, str, str, str, (int, int, int): original word, rasmised word in Latin, rasmised word in Arabic, paleo-orthographic representation of word, Quran index e.g.

            ("إِنَّمَآ", "ABMA", "اٮما", "AɂᵢB’ᵚᵃMᵃA˜", (20, 98, 1))
            ("إِلَٰهُكُمُ", "ALHKM", "الهکم", "AɂᵢLᵃᴬHᵘKᵘMᵘ", (20, 98, 2))
            ("ٱللَّهُ", "ALLH", "الله", "ALLᵚᵃHᵘ", (20, 98, 3))
            ("ٱلَّذِی", "ALDY", "الدی", "AᵟLᵚᵃD’ᵢY", (20, 98, 4))
            ("لَآ", "LA", "لا", "LᵃA˜", (20, 98, 5))
            ("إِلَٰهَ", "ALH", "اله", "Aɂᵢ LᵃᴬHᵃ", (20, 98, 6))
            ("إِلَّا", "ALA", "الا", "Aɂᵢ LᵚᵃA", (20, 98, 7))
            ("هُوَۚ", "HW", "هو", "HᵘWᵃ⒥", (20, 98, 8))
        
    Yield:
        (if uniq==False and blocks==True and paleo==True)
        str, list: original word, list of of blocks in Latin transcription, Arabic script, paleo-orthographic representation and Quranic index, e.g.

            ("إِنَّمَآ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 1, 1)), ("نَّمَآ", "BMA", "ٮما", "B’ᵚᵃMᵃA˜", (20, 98, 1, 2))])
            ("إِلَٰهُكُمُ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 2, 1)), ("لَٰهُكُمُ", "LHKM", "لهکم", "LᵃᴬHᵘKᵘMᵘ", (20, 98, 2, 2))])
            ("ٱللَّهُ", [("ٱ", "A", "ا", "A", (20, 98, 3, 1)), ("للَّهُ", "LLH", "لله", "LLᵚᵃHᵘ", (20, 98, 3, 2))])
            ("ٱلَّذِی", [("ٱ", "A", "ا", "Aᵟ", (20, 98, 4, 1)), ("لَّذِ", "LD", "لد", "LᵚᵃD’ᵢ", (20, 98, 4, 2)), ("ی", "Y", "ی", "Y", (20, 98, 4, 3))])
            ("لَآ", [("لَآ", "LA", "لا", "LᵃA˜", (20, 98, 5, 1))])
            ("إِلَٰهَ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 6, 1)), ("لَٰهَ", "LH", "له", "LᵃᴬHᵃ", (20, 98, 6, 2))])
            ("إِلَّا", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 7, 1)), ("لَّا", "LA", "لا", "LᵚᵃA", (20, 98, 7, 2))])
            ("هُوَۚ", [("هُوَۚ", "HW", "هو", "HᵘWᵃ⒥", (20, 98, 8, 1))])

    Yield:
        (if uniq==False and blocks==True and paleo==False)
        str, list: original word, list of of blocks in Latin transcription, Arabic script and Quranic index, e.g.

            ("إِنَّمَآ", [("إِ", "A", "ا", (20, 98, 1, 1)), ("نَّمَآ", "BMA", "ٮما", (20, 98, 1, 2))])
            ("إِلَٰهُكُمُ", [("إِ", "A", "ا", (20, 98, 2, 1)), ("لَٰهُكُمُ", "LHKM", "لهکم", (20, 98, 2, 2))])
            ("ٱللَّهُ", [("ٱ", "A", "ا", (20, 98, 3, 1)), ("للَّهُ", "LLH", "لله", (20, 98, 3, 2))])
            ("ٱلَّذِی", [("ٱ", "A", "ا", (20, 98, 4, 1)), ("لَّذِ", "LD", "لد", (20, 98, 4, 2)), ("ی", "Y", "ی", (20, 98, 4, 3))])
            ("لَآ", [("لَآ", "LA", "لا", (20, 98, 5, 1))])
            ("إِلَٰهَ", [("إِ", "A", "ا", (20, 98, 6, 1)), ("لَٰهَ", "LH", "له", (20, 98, 6, 2))])
            ("إِلَّا", [("إِ", "A", "ا", (20, 98, 7, 1)), ("لَّا", "LA", "لا", (20, 98, 7, 2))])
            ("هُوَۚ", [("هُوَۚ", "HW", "هو", "HᵘWᵃ⒥", (20, 98, 8, 1))])

    Yield:
        (if uniq==True and paleo==False ; blocks is irrelevant)
        str, str, int, set: rasmised block in Latin, rasmised block in Arabic, total occurrences of block, list of unique types where it appears, e.g.
            ("A", "ا", 6, {"إِلَّا", "ٱلَّذِی", "إِنَّمَآ", "إِلَٰهَ", "إِلَٰهُكُمُ", "ٱللَّهُ"})
            ("LA", "لا", 2, {"إِلَّا", "لَآ"})
            ("BMA", "ٮما", 1, {"إِنَّمَآ"})
            ("HW", "هو", 1, {"هُوَۚ"})
            ("LD", "لد", 1, {"ٱلَّذِی"})
            ("LH", "له", 1, {"إِلَٰهَ"})
            ("LHKM", "لهکم", 1, {"إِلَٰهُكُمُ"})
            ("LLH", "لله", 1, {"ٱللَّهُ"})
            ("Y", "ی", 1, {"ٱلَّذِی"})

    Yield:
        (if uniq==True and paleo==False ; blocks is irrelevant)
        str, str, int, set: rasmised block in Latin, rasmised block in Arabic, total occurrences of block, list of unique types where it appears, e.g.
            ("A", "ا", 6, {("إِلَّا", "Aɂᵢ LᵚᵃA"), ("ٱلَّذِی", "Aᵟ LᵚᵃD’ᵢ Y"), ("إِنَّمَآ", "Aɂᵢ B’ᵚᵃMᵃA˜"), ("إِلَٰهَ", "Aɂᵢ LᵃᴬHᵃ"), ("إِلَٰهُكُمُ", "Aɂᵢ LᵃᴬHᵘKᵘMᵘ"), ("ٱللَّهُ", "A LLᵚᵃHᵘ")})
            ("LA", "لا", 2, {("إِلَّا", "Aɂᵢ LᵚᵃA"), ("لَآ", "LᵃA˜")})
            ("BMA", "ٮما", 1, {("إِنَّمَآ", "Aɂᵢ B’ᵚᵃMᵃA˜")})
            ("HW", "هو", 1, {("هُوَۚ", "HᵘWᵃ⒥")})
            ("LD", "لد", 1, {("ٱلَّذِی", "Aᵟ LᵚᵃD’ᵢ Y")})
            ("LH", "له", 1, {("إِلَٰهَ", "Aɂᵢ LᵃᴬHᵃ")})
            ("LHKM", "لهکم", 1, {("إِلَٰهُكُمُ", "Aɂᵢ LᵃᴬHᵘKᵘMᵘ")})
            ("LLH", "لله", 1, {("ٱللَّهُ", "A LLᵚᵃHᵘ")})
            ("Y", "ی", 1, {("ٱلَّذِی", "Aᵟ LᵚᵃD’ᵢ Y")})

    Raise:
        IndexError: Quran index out of range.
        PrivateFileError: decotype file is private.

    """
    if uniq and blocks:
        blocks = False

    try:
        blocks_quran = _get_blocks(input_, source, only_rasm)

        # group blocks into words
        blocks_gr = (list(gr) for _, gr in groupby(blocks_quran, key=lambda x: (x[1][1], x[1][2])))

        if not blocks:

            if uniq:
                if paleo:
                    yield from _uniq(((''.join(g[0][0] for g in b), ' '.join(g[0][1] for g in b),
                                       ' '.join(g[0][2] for g in b), ''.join(g[0][3] for g in b)) for b in blocks_gr), paleo=paleo)
                else:
                    yield from _uniq(((''.join(g[0][0] for g in b), ' '.join(g[0][1] for g in b), ' '.join(g[0][2] for g in b)) for b in blocks_gr))

            elif paleo:
                yield from ((''.join(g[0][0] for g in b), ''.join(g[0][1] for g in b), ''.join(g[0][2] for g in b),
                    ''.join(g[0][3] for g in b), b[0][1][:-1]) for b in blocks_gr)

            # blocks==False, paleo==True
            else:
                yield from ((''.join(g[0][0] for g in b), ''.join(g[0][1] for g in b), ''.join(g[0][2] for g in b), b[0][1][:-1]) for b in blocks_gr)

        else:
            if paleo:
                yield from ((''.join(g[0][0] for g in b), [(*g[0], g[1]) for g in b]) for b in blocks_gr)

            else:
                yield from ((''.join(g[0][0] for g in b), [(*g[0][:-1], g[1]) for g in b]) for b in blocks_gr)

    except PrivateFileError:
        raise PrivateFileError
    except IndexError:
        raise IndexError

