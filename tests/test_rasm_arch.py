#!/usr/bin/env python3
#
#    test_rasm_arch.py                                    ا
#                                                   ح   ه
#                                                  ف   ذ   ا   
#                                                 ظ   ا   ل   ي   
#                                                ز       م   ا   ك   
#                                                       ص       ب
#                                                      و       ي
#                                                     د       ك
#                                                    ر       ج      
# usage:
#   pass all tests:
#     $ python3 -m pytest test_rasm_arch.py
#   pass specific test:
#     $ python3 -m pytest test_rasm_arch.py::Test_Rasm_Input_Index_Tanzeel::test_7 -vv
#
# profiling:
#   $ hyperfine 'rasm_arch --text <(echo فوو) --paleo --blocks' --warmup 1
#   $ find ~/Documents/openITI/RELEASE/data -name *-ara1 -exec cat {} + | rasm --blocks | wc -l
#
# MIT License
# 
# Copyright (c) 2022 Alicia González Martínez
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
###############################################################################################

import io
import pytest
from argparse import ArgumentParser
from importlib.resources import files

from rasm_arch import rasm_arch as rasm
from rasm_arch.util import SOURCE


RESOURSE_EXISTS = files("rasm_arch_data").joinpath(SOURCE.DECOTYPE).exists()


class Test_Rasm_Input_Text:

    def test_1(self):
        list(rasm(io.StringIO("كبيكج وكيتكج والجِنّ"), paleo=False, blocks=False, uniq=False, norm_clusters=False)) \
            == [("كبيكج", "KBBKG", "كٮٮكح"),
                ("وكيتكج", "WKBBKG", "وكٮٮكح"),
                ("والجِنّ", "WALGN", "والحں")]

    def test_2(self):
        list(rasm(io.StringIO("كبيكج وكيتكج والجِنّ"), paleo=True, blocks=False, uniq=False, norm_clusters=False)) \
            == [("كبيكج", "KBBKG", "كٮٮكح", "KB₁B₂KG₁"),
                ("وكيتكج", "WKBBKG", "وكٮٮكح", "WKB₂B²KG₁"),
                ("والجِنّ", "WALGN", "والحں", "WALG₁ᵢN¹ᵚ")]
    
    def test_3(self):
        list(rasm(io.StringIO("كبيكج وكيتكج والجِنّ"), paleo=False, blocks=True, uniq=False, norm_clusters=False)) \
            == [("كبيكج", [("كبيكج", "KBBKG", "كٮٮكح")]),
                ("وكيتكج", [("و", "W", "و"), ("كيتكج", "KBBKG", "كٮٮكح")]),
                ("والجِنّ", [("و", "W", "و"), ("ا", "A", "ا"), ("لجِنّ", "LGN", "لحں")])]

    def test_4(self):
        list(rasm(io.StringIO("كبيكج وكيتكج والجِنّ"), paleo=True, blocks=True, uniq=False, norm_clusters=False)) \
            == [("كبيكج", [("كبيكج", "KBBKG", "كٮٮكح", "KB₁B₂KG₁")]),
                ("وكيتكج", [("و", "W", "و", "W"), ("كيتكج", "KBBKG", "كٮٮكح", "KB₂B²KG₁")]),
                ("والجِنّ", [("و", "W", "و", "W"), ("ا", "A", "ا", "A"), ("لجِنّ", "LGN", "لحں", "LG₁ᵢN¹ᵚ")])]

    def test_5(self):
        list(rasm(io.StringIO("كبيكج وكيتكج والجِنّ"), paleo=False, blocks=False, uniq=True, norm_clusters=False)) \
            == [("KBBKG", "كٮٮكح", 2, {"كبيكج", "وكيتكج"}),
                ("W", "و", 2, {"وكيتكج", "والجِنّ"}),
                ("A", "ا", 1, {"والجِنّ"}),
                ("LGN", "لحں", 1, {"والجِنّ"})]

    def test_6(self):
        list(rasm(io.StringIO("كبيكج وكيتكج والجِنّ"), paleo=True, blocks=True, uniq=True, norm_clusters=False)) \
            == [("KBBKG", "كٮٮكح", 2, {("كبيكج", "KB₁B₂KG₁"), ("وكيتكج", "WKB₂B²KG₁")}),
                ("W", "و", 2, {("وكيتكج", "WKB₂B²KG₁"), ("والجِنّ", "WALG₁ᵢN¹ᵚ")}),
                ("A", "ا", 1, {("والجِنّ", "WALG₁ᵢN¹ᵚ")}),
                ("LGN", "لحں", 1, {("والجِنّ", "WALG₁ᵢN¹ᵚ")})]


class Test_Rasm_Input_Index_Tanzeel:
    
    def test_1(self):

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="tanzil-uthmani", paleo=False, blocks=False, uniq=False))
        expected = [("إِنَّمَآ", "ABMA", "اٮما", (20, 98, 1)),
                    ("إِلَٰهُكُمُ", "ALHKM", "الهكم", (20, 98, 2)),
                    ("ٱللَّهُ", "ALLH", "الله", (20, 98, 3)),
                    ("ٱلَّذِى", "ALDY", "الدی", (20, 98, 4)),
                    ("لَآ", "LA", "لا", (20, 98, 5)),
                    ("إِلَٰهَ", "ALH", "اله", (20, 98, 6)),
                    ("إِلَّا", "ALA", "الا", (20, 98, 7)),
                    ("هُوَۚ", "HW", "هو", (20, 98, 8))]

        assert result == expected

    
    def test_2(self):

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="tanzil-uthmani", paleo=True, blocks=False, uniq=False))

        expected = [("إِنَّمَآ", "ABMA", "اٮما", "AɂᵢB¹ᵚᵃMᵃA˜", (20, 98, 1)),
                    ("إِلَٰهُكُمُ", "ALHKM", "الهكم", "AɂᵢLᵃᴬHᵘKᵘMᵘ", (20, 98, 2)),
                    ("ٱللَّهُ", "ALLH", "الله", "AᵟLLᵚᵃHᵘ", (20, 98, 3)),
                    ("ٱلَّذِى", "ALDY", "الدی", "AᵟLᵚᵃD¹ᵢY", (20, 98, 4)),
                    ("لَآ", "LA", "لا", "LᵃA˜", (20, 98, 5)),
                    ("إِلَٰهَ", "ALH", "اله", "AɂᵢLᵃᴬHᵃ", (20, 98, 6)),
                    ("إِلَّا", "ALA", "الا", "AɂᵢLᵚᵃA", (20, 98, 7)),
                    ("هُوَۚ", "HW", "هو", "HᵘWᵃ⒥", (20, 98, 8))]

        assert result == expected


    def test_3(self):

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)),  source="tanzil-uthmani", paleo=False, blocks=True, uniq=False))
        expected = [("إِنَّمَآ", [("إِ", "A", "ا", (20, 98, 1, 1)), ("نَّمَآ", "BMA", "ٮما", (20, 98, 1, 2))]),
                    ("إِلَٰهُكُمُ", [("إِ", "A", "ا", (20, 98, 2, 1)), ("لَٰهُكُمُ", "LHKM", "لهكم", (20, 98, 2, 2))]),
                    ("ٱللَّهُ", [("ٱ", "A", "ا", (20, 98, 3, 1)), ("للَّهُ", "LLH", "لله", (20, 98, 3, 2))]),
                    ("ٱلَّذِى", [("ٱ", "A", "ا", (20, 98, 4, 1)), ("لَّذِ", "LD", "لد", (20, 98, 4, 2)),
                              ("ى", "Y", "ی", (20, 98, 4, 3))]),
                    ("لَآ", [("لَآ", "LA", "لا", (20, 98, 5, 1))]),
                    ("إِلَٰهَ", [("إِ", "A", "ا", (20, 98, 6, 1)), ("لَٰهَ", "LH", "له", (20, 98, 6, 2))]),
                    ("إِلَّا", [("إِ", "A", "ا", (20, 98, 7, 1)), ("لَّا", "LA", "لا", (20, 98, 7, 2))]),
                    ("هُوَۚ", [("هُوَۚ", "HW", "هو", (20, 98, 8, 1))])]

        assert result == expected


    def test_4(self):

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="tanzil-uthmani", paleo=True, blocks=True, uniq=False))
        expected = [("إِنَّمَآ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 1, 1)), ("نَّمَآ", "BMA", "ٮما", "B¹ᵚᵃMᵃA˜", (20, 98, 1, 2))]),
                    ("إِلَٰهُكُمُ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 2, 1)), ("لَٰهُكُمُ", "LHKM", "لهكم", "LᵃᴬHᵘKᵘMᵘ", (20, 98, 2, 2))]),
                    ("ٱللَّهُ", [("ٱ", "A", "ا", "Aᵟ", (20, 98, 3, 1)), ("للَّهُ", "LLH", "لله", "LLᵚᵃHᵘ", (20, 98, 3, 2))]),
                    ("ٱلَّذِى", [("ٱ", "A", "ا", "Aᵟ", (20, 98, 4, 1)), ("لَّذِ", "LD", "لد", "LᵚᵃD¹ᵢ", (20, 98, 4, 2)),
                              ("ى", "Y", "ی", "Y", (20, 98, 4, 3))]),
                    ("لَآ", [("لَآ", "LA", "لا", "LᵃA˜", (20, 98, 5, 1))]),
                    ("إِلَٰهَ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 6, 1)), ("لَٰهَ", "LH", "له", "LᵃᴬHᵃ", (20, 98, 6, 2))]),
                    ("إِلَّا", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 7, 1)), ("لَّا", "LA", "لا", "LᵚᵃA", (20, 98, 7, 2))]),
                    ("هُوَۚ", [("هُوَۚ", "HW", "هو", "HᵘWᵃ⒥", (20, 98, 8, 1))])]

        assert result == expected


    def test_5(self):

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="tanzil-uthmani", paleo=False, blocks=False, uniq=True))
        expected = [("A", "ا", 6, {"إِلَّا", "ٱلَّذِى", "إِنَّمَآ", "إِلَٰهَ", "إِلَٰهُكُمُ", "ٱللَّهُ"}),
                    ("LA", "لا", 2, {"إِلَّا", "لَآ"}),
                    ("BMA", "ٮما", 1, {"إِنَّمَآ"}),
                    ("HW", "هو", 1, {"هُوَۚ"}),
                    ("LD", "لد", 1, {"ٱلَّذِى"}),
                    ("LH", "له", 1, {"إِلَٰهَ"}),
                    ("LHKM", "لهكم", 1, {"إِلَٰهُكُمُ"}),
                    ("LLH", "لله", 1, {"ٱللَّهُ"}),
                    ("Y", "ی", 1, {"ٱلَّذِى"})]

        assert result == expected


    def test_6(self):

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="tanzil-uthmani", paleo=True, blocks=False, uniq=True))
        expected = [("A", "ا", 6, {("إِلَّا", "AɂᵢLᵚᵃA"), ("ٱلَّذِى", "AᵟLᵚᵃD¹ᵢY"), ("إِنَّمَآ", "AɂᵢB¹ᵚᵃMᵃA˜"), ("إِلَٰهَ", "AɂᵢLᵃᴬHᵃ"),
                                   ("إِلَٰهُكُمُ", "AɂᵢLᵃᴬHᵘKᵘMᵘ"), ("ٱللَّهُ", "AᵟLLᵚᵃHᵘ")}),
                    ("LA", "لا", 2, {("إِلَّا", "AɂᵢLᵚᵃA"), ("لَآ", "LᵃA˜")}),
                    ("BMA", "ٮما", 1, {("إِنَّمَآ", "AɂᵢB¹ᵚᵃMᵃA˜")}),
                    ("HW", "هو", 1, {("هُوَۚ", "HᵘWᵃ⒥")}),
                    ("LD", "لد", 1, {("ٱلَّذِى", "AᵟLᵚᵃD¹ᵢY")}),
                    ("LH", "له", 1, {("إِلَٰهَ", "AɂᵢLᵃᴬHᵃ")}),
                    ("LHKM", "لهكم", 1, {("إِلَٰهُكُمُ", "AɂᵢLᵃᴬHᵘKᵘMᵘ")}),
                    ("LLH", "لله", 1, {("ٱللَّهُ", "AᵟLLᵚᵃHᵘ")}),
                    ("Y", "ی", 1, {("ٱلَّذِى", "AᵟLᵚᵃD¹ᵢY")})]

        assert result == expected


    def test_7(self):

        result = list(rasm(((53, 62, 3, None), (54, 1, 1, None)), source="tanzil-uthmani", paleo=False, blocks=False, uniq=False))
        expected = [("وَٱعْبُدُوا۟", 'WAEBDWA', "واعٮدوا", (53, 62, 3)), ("۩", "", "", (53, 62, 4)), ("بِسْمِ", "BSM", "ٮسم", (54, 1, 1))]

        assert result == expected


class Test_Rasm_Input_Index_DT:

    
    def test_1(self):

        if not RESOURSE_EXISTS:
            pytest.skip("module not tested", allow_module_level=True)

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="decotype", paleo=False, blocks=False, uniq=False))
        expected = [("إِنَّمَآ", "ABMA", "اٮما", (20, 98, 1)),
                    ("إِلَٰهُكُمُ", "ALHKM", "الهكم", (20, 98, 2)),
                    ("ٱللَّهُ", "ALLH", "الله", (20, 98, 3)),
                    ("ٱلَّذِی", "ALDY", "الدی", (20, 98, 4)),
                    ("لَآ", "LA", "لا", (20, 98, 5)),
                    ("إِلَٰهَ", "ALH", "اله", (20, 98, 6)),
                    ("إِلَّا", "ALA", "الا", (20, 98, 7)),
                    ("هُوَۚ", "HW", "هو", (20, 98, 8))]

        assert result == expected

    
    def test_2(self):

        if not RESOURSE_EXISTS:
            pytest.skip("module not tested", allow_module_level=True)

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="decotype", paleo=True, blocks=False, uniq=False))

        expected = [("إِنَّمَآ", "ABMA", "اٮما", "AɂᵢB¹ᵚᵃMᵃA˜", (20, 98, 1)),
                    ("إِلَٰهُكُمُ", "ALHKM", "الهكم", "AɂᵢLᵃᴬHᵘKᵘMᵘ", (20, 98, 2)),
                    ("ٱللَّهُ", "ALLH", "الله", "AᵟLLᵚᵃHᵘ", (20, 98, 3)),
                    ("ٱلَّذِی", "ALDY", "الدی", "AᵟLᵚᵃD¹ᵢY", (20, 98, 4)),
                    ("لَآ", "LA", "لا", "LᵃA˜", (20, 98, 5)),
                    ("إِلَٰهَ", "ALH", "اله", "AɂᵢLᵃᴬHᵃ", (20, 98, 6)),
                    ("إِلَّا", "ALA", "الا", "AɂᵢLᵚᵃA", (20, 98, 7)),
                    ("هُوَۚ", "HW", "هو", "HᵘWᵃ⒥", (20, 98, 8))]

        assert result == expected


    def test_3(self):

        if not RESOURSE_EXISTS:
            pytest.skip("module not tested", allow_module_level=True)

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)),  source="decotype", paleo=False, blocks=True, uniq=False))
        expected = [("إِنَّمَآ", [("إِ", "A", "ا", (20, 98, 1, 1)), ("نَّمَآ", "BMA", "ٮما", (20, 98, 1, 2))]),
                    ("إِلَٰهُكُمُ", [("إِ", "A", "ا", (20, 98, 2, 1)), ("لَٰهُكُمُ", "LHKM", "لهكم", (20, 98, 2, 2))]),
                    ("ٱللَّهُ", [("ٱ", "A", "ا", (20, 98, 3, 1)), ("للَّهُ", "LLH", "لله", (20, 98, 3, 2))]),
                    ("ٱلَّذِی", [("ٱ", "A", "ا", (20, 98, 4, 1)), ("لَّذِ", "LD", "لد", (20, 98, 4, 2)),
                              ("ی", "Y", "ی", (20, 98, 4, 3))]),
                    ("لَآ", [("لَآ", "LA", "لا", (20, 98, 5, 1))]),
                    ("إِلَٰهَ", [("إِ", "A", "ا", (20, 98, 6, 1)), ("لَٰهَ", "LH", "له", (20, 98, 6, 2))]),
                    ("إِلَّا", [("إِ", "A", "ا", (20, 98, 7, 1)), ("لَّا", "LA", "لا", (20, 98, 7, 2))]),
                    ("هُوَۚ", [("هُوَۚ", "HW", "هو", (20, 98, 8, 1))])]

        assert result == expected


    def test_4(self):

        if not RESOURSE_EXISTS:
            pytest.skip("module not tested", allow_module_level=True)

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="decotype", paleo=True, blocks=True, uniq=False))
        expected = [("إِنَّمَآ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 1, 1)), ("نَّمَآ", "BMA", "ٮما", "B¹ᵚᵃMᵃA˜", (20, 98, 1, 2))]),
                    ("إِلَٰهُكُمُ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 2, 1)), ("لَٰهُكُمُ", "LHKM", "لهكم", "LᵃᴬHᵘKᵘMᵘ", (20, 98, 2, 2))]),
                    ("ٱللَّهُ", [("ٱ", "A", "ا", "Aᵟ", (20, 98, 3, 1)), ("للَّهُ", "LLH", "لله", "LLᵚᵃHᵘ", (20, 98, 3, 2))]),
                    ("ٱلَّذِی", [("ٱ", "A", "ا", "Aᵟ", (20, 98, 4, 1)), ("لَّذِ", "LD", "لد", "LᵚᵃD¹ᵢ", (20, 98, 4, 2)),
                              ("ی", "Y", "ی", "Y", (20, 98, 4, 3))]),
                    ("لَآ", [("لَآ", "LA", "لا", "LᵃA˜", (20, 98, 5, 1))]),
                    ("إِلَٰهَ", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 6, 1)), ("لَٰهَ", "LH", "له", "LᵃᴬHᵃ", (20, 98, 6, 2))]),
                    ("إِلَّا", [("إِ", "A", "ا", "Aɂᵢ", (20, 98, 7, 1)), ("لَّا", "LA", "لا", "LᵚᵃA", (20, 98, 7, 2))]),
                    ("هُوَۚ", [("هُوَۚ", "HW", "هو", "HᵘWᵃ⒥", (20, 98, 8, 1))])]

        assert result == expected


    def test_5(self):

        if not RESOURSE_EXISTS:
            pytest.skip("module not tested", allow_module_level=True)

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="decotype", paleo=False, blocks=False, uniq=True))
        expected = [("A", "ا", 6, {"إِلَّا", "ٱلَّذِی", "إِنَّمَآ", "إِلَٰهَ", "إِلَٰهُكُمُ", "ٱللَّهُ"}),
                    ("LA", "لا", 2, {"إِلَّا", "لَآ"}),
                    ("BMA", "ٮما", 1, {"إِنَّمَآ"}),
                    ("HW", "هو", 1, {"هُوَۚ"}),
                    ("LD", "لد", 1, {"ٱلَّذِی"}),
                    ("LH", "له", 1, {"إِلَٰهَ"}),
                    ("LHKM", "لهكم", 1, {"إِلَٰهُكُمُ"}),
                    ("LLH", "لله", 1, {"ٱللَّهُ"}),
                    ("Y", "ی", 1, {"ٱلَّذِی"})]

        assert result == expected


    def test_6(self):

        if not RESOURSE_EXISTS:
            pytest.skip("module not tested", allow_module_level=True)

        result = list(rasm(((20, 98, None, None), (20, 98, 8, None)), source="decotype", paleo=True, blocks=False, uniq=True))
        expected = [("A", "ا", 6, {("إِلَّا", "AɂᵢLᵚᵃA"), ("ٱلَّذِی", "AᵟLᵚᵃD¹ᵢY"), ("إِنَّمَآ", "AɂᵢB¹ᵚᵃMᵃA˜"), ("إِلَٰهَ", "AɂᵢLᵃᴬHᵃ"),
                                   ("إِلَٰهُكُمُ", "AɂᵢLᵃᴬHᵘKᵘMᵘ"), ("ٱللَّهُ", "AᵟLLᵚᵃHᵘ")}),
                    ("LA", "لا", 2, {("إِلَّا", "AɂᵢLᵚᵃA"), ("لَآ", "LᵃA˜")}),
                    ("BMA", "ٮما", 1, {("إِنَّمَآ", "AɂᵢB¹ᵚᵃMᵃA˜")}),
                    ("HW", "هو", 1, {("هُوَۚ", "HᵘWᵃ⒥")}),
                    ("LD", "لد", 1, {("ٱلَّذِی", "AᵟLᵚᵃD¹ᵢY")}),
                    ("LH", "له", 1, {("إِلَٰهَ", "AɂᵢLᵃᴬHᵃ")}),
                    ("LHKM", "لهكم", 1, {("إِلَٰهُكُمُ", "AɂᵢLᵃᴬHᵘKᵘMᵘ")}),
                    ("LLH", "لله", 1, {("ٱللَّهُ", "AᵟLLᵚᵃHᵘ")}),
                    ("Y", "ی", 1, {("ٱلَّذِی", "AᵟLᵚᵃD¹ᵢY")})]

        assert result == expected


    def test_7(self):

        if not RESOURSE_EXISTS:
            pytest.skip("module not tested", allow_module_level=True)

        result = list(rasm(((53, 62, 3, None), (54, 1, 1, None)), source="decotype", paleo=False, blocks=False, uniq=False))
        expected = [("وَٱعۡبُدُوا۟", "WAEBDWA", "واعٮدوا", (53, 62, 3)), ("۩", "", "", (53, 62, 4)), ("بِسۡمِ", "BSM", "ٮسم", (54, 1, 1))]

        assert result == expected


class Test_Rasm_More:

    def test_1(self):
        result = list(rasm(io.StringIO("بيت"), paleo=False, blocks=False, uniq=False, norm_clusters=False))
        expected = [("بيت", "BBB", "ٮٮٮ")]
        assert result == expected        

    def test_2(self):
        result = list(rasm(io.StringIO("بنن"), paleo=False, blocks=False, uniq=False, norm_clusters=False))
        expected = [('بنن', 'BBN', 'ٮٮں')]
        assert result == expected


class Test_Rasm_Letterblock_Spaces:

    def test_1(self):
        result = list(rasm(io.StringIO("بھارت"), paleo=False, blocks=False, uniq=False, norm_clusters=False, sep_blocks=True))
        expected = [("بھارت", "BOA R B", "ٮھا ر ٮ")]
        assert result == expected


    def test_2(self):
        result = list(rasm(((53, 62, 3, None), (54, 1, 1, None)), source="tanzil-uthmani", paleo=False, blocks=False,
                                                                  uniq=False, sep_blocks=True))
        expected = [("وَٱعْبُدُوا۟", 'W A EBD W A', "و ا عٮد و ا", (53, 62, 3)),
                    ("۩", "", "", (53, 62, 4)), ("بِسْمِ", "BSM", "ٮسم", (54, 1, 1))]
        assert result == expected


class Test_Rasm_Urdu:

    def test_1(self):
        result = list(rasm(io.StringIO("بھارت"), paleo=False, blocks=False, uniq=False, norm_clusters=False))
        expected = [("بھارت", "BOARB", "ٮھارٮ")]
        assert result == expected

    def test_2(self):
        result = list(rasm(io.StringIO("ہے۔"), paleo=False, blocks=False, uniq=False, norm_clusters=False))
        expected = [("ہے۔", "HJ", "هے")]
        assert result == expected


# O = ھ   # ھ U+06be ARABIC LETTER HEH DOACHASHMEE
# J = ے   # ے U+06d2 ARABIC LETTER YEH BARREE

