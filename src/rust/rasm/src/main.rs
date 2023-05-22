/*
 *    rasm.rs
 * 
 *
 * MIT License
 * 
 * Copyright (c) 2022 Alicia González Martínez
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * creation of project:
 *   $ cargo new rasm --bin
 *
 * use as a script:
 *   Add shebang: #!/usr/bin/env run-cargo-script
 *   make script executable: $ chmod +x main.rs
 *   execute: $ ./main.rs
 *
 * usage:
 *   $ RUSTFLAGS="$RUSTFLAGS -A dead_code" cargo build && ./target/debug/rasm --infile <(echo -e "بِسۡمِ ﷲ ٱلرَّحۡمَٰنِ\nٱلرَّحِيمِ\nٱلرَّحۡمَٰنِ ٱلaaرَّحِيمِ")
 *   OR
 *   $ cargo run -- --infile <(echo -e "بِسۡمِ ﷲ ٱلرَّحۡمَٰنِ\nٱلرَّحِيمِ\nٱلرَّحۡمَٰنِ ٱلaaرَّحِيمِ")
 *
 ************************************************************************************************************/

#![allow(non_snake_case)]

#[macro_use] extern crate maplit;
extern crate argparse;
extern crate regex;

#[macro_use(c)]
extern crate cute;

use std::io::prelude::*;
use std::io::{BufReader, Result};
use std::fs::File;

use std::process;
use std::collections::HashMap;
use argparse::{ArgumentParser, StoreTrue, Store};
use regex::{Captures, Regex};

#[derive(Debug)]
struct Arachars {
    Q: &'static str,
    N: &'static str,
    Y: &'static str,
    A: &'static str,
    B: &'static str,
    G: &'static str,
    R: &'static str,
    D: &'static str,
    T: &'static str,
    C: &'static str,
    S: &'static str,
    F: &'static str,
    E: &'static str,
    W: &'static str,
    H: &'static str,
    M: &'static str,
    L: &'static str,
    K: &'static str,
    diac: &'static str,
    clusters: HashMap<&'static str, &'static str>,
}

#[derive(Debug)]
struct Mappings {
    mapping_end: HashMap<String, String>,
    mapping_gen: HashMap<String, String>,
    mapping_ara: HashMap<&'static str, &'static str>,
}

fn load_rasm_mappings(arachars: &Arachars) -> Mappings {

    Mappings {

        mapping_end: c!{c.to_string() => "Q".to_string(), for c in arachars.Q.chars()}.into_iter()
              .chain(c!{c.to_string() => "N".to_string(), for c in arachars.N.chars()}).into_iter()
              .chain(c!{c.to_string() => "Y".to_string(), for c in arachars.Y.chars()}).collect(),

        mapping_gen: c!{c.to_string() => "B".to_string(), for c in (arachars.N.chars().as_str().to_string().clone() +
                                                                  &(arachars.Y.chars().as_str().to_string()) + 
                                                                  &(arachars.B.chars().as_str().to_string())).chars()}.into_iter()
              .chain(c!{c.to_string() => "G".to_string(), for c in arachars.G.chars()}).into_iter()
              .chain(c!{c.to_string() => "T".to_string(), for c in arachars.T.chars()}).into_iter()
              .chain(c!{c.to_string() => "C".to_string(), for c in arachars.C.chars()}).into_iter()
              .chain(c!{c.to_string() => "S".to_string(), for c in arachars.S.chars()}).into_iter()
              .chain(c!{c.to_string() => "F".to_string(), for c in arachars.F.chars()}).into_iter()
              .chain(c!{c.to_string() => "E".to_string(), for c in arachars.E.chars()}).into_iter()
              .chain(c!{c.to_string() => "H".to_string(), for c in arachars.H.chars()}).into_iter()
              .chain(c!{c.to_string() => "M".to_string(), for c in arachars.M.chars()}).into_iter()
              .chain(c!{c.to_string() => "L".to_string(), for c in arachars.L.chars()}).into_iter()
              .chain(c!{c.to_string() => "K".to_string(), for c in arachars.K.chars()}).into_iter()
              .chain(c!{c.to_string() => "A ".to_string(), for c in arachars.A.chars()}).into_iter()
              .chain(c!{c.to_string() => "R ".to_string(), for c in arachars.R.chars()}).into_iter()
              .chain(c!{c.to_string() => "D ".to_string(), for c in arachars.D.chars()}).into_iter()
              .chain(c!{c.to_string() => "W ".to_string(), for c in arachars.T.chars()}).collect(),

        mapping_ara: hashmap! {
                    "Q" => "ٯ" ,
                    "N" => "ں" ,
                    "Y" => "ی" ,
                    "B" => "ٮ" ,
                    "G" => "ح" ,
                    "T" => "ط" ,
                    "C" => "ص" ,
                    "S" => "س" ,
                    "F" => "ڡ" ,
                    "E" => "ع" ,
                    "H" => "ه" ,
                    "M" => "م" ,
                    "L" => "ل" ,
                    "K" => "ک" ,
                    "A" => "ا" ,
                    "R" => "ر" ,
                    "D" => "د" ,
                    "W" => "و" ,
        },
    }
}


fn load_arabic_inventory() -> Arachars {

    Arachars {

        Q: "ٯࢥڧقڨﻕﻖفﻑﻒ",
        N: "ںنڻڼڹݧݨݩڽﻥﻦ",
        Y: "ىیۍݷيېۑؠئؽێݵݶࢨࢩؾؿےۓݺݻﻯﻰﮮﮯیﯼﯽﻲﮰﮱﺉﺊ",
        A: "ٱأإآاٳٲݳݴٵﺃﺄﺇﺈﺁﺂﺍﺎﭐﭑﴼ",
        B: "ࢬٮبݕࢠٻݐپڀݒٹݖݔتٺټݓثٽٿݑﻧﻨﯾﯿﻳﻴۦﺋﺌﺏﺐﺑﺒﭖﭗﭘﭙﺕﺖﺗﺘﺙﺚﺛﺜٮ",
        G: "خحجچݮݼڃڄچڇݘݯځݲڿڂݗࢢڅﺝﺞﺟﺠﺡﺢﺣﺤﺥﺦﺧﺨﭺﭻﭼﭽ",
        R: "رزړݛࢪڔڕڑڒۯݬږڗݫژڙݱﺭﺮﺯﺰﮊﮋ",
        D: "دذڈډڊݚڍڈۮڋݙڌڎڏڐﺩﺪﺫﺬ",
        T: "طظࢣڟﻁﻂﻃﻄﻅﻆﻇﻈ",
        C: "صضڝۻڞﺹﺺﺻﺼﺽﺾﺿﻀ",
        S: "سشڛݽݾښݭݜݰۺڜﺱﺲﺳﺴﺵﺶﺷﺸ",
        F: "ڡڢݠڥݡڣڤڦࢤﻓﻔﻗﻘ",
        E: "عغۼݝݟڠݞﻉﻊﻋﻌﻍﻎﻏﻐ",
        W: "وۄۅࢫؤۆۇۈۉۏݸݹۊۋﻭﻮﺅﺆ",
        H: "هھہەۀۂۿةۃﮤﮥﺓﺔﮦﮧﮨﮩﻪﻫﻬﮪﮫﮬﮭ",
        M: "مݦݥࢧﻡﻢﻣﻤ",
        L: "لݪࢦڸڵڶڷﻝﻞﻟﻠ",
        K: "كکڪګگڰڲڳؼڮݤڮݢػڱݿڭڴݣﻙﻚﻛﻜکﮎﮏﮐﮑﮒﮓﮔﮕ",
        
        diac: "ءـًٌٍَُِّٰٕۣٓۤٔۜ۟۠ۡۢۥۦࣰࣱࣲْ۪ۭۧۨ۫۬ﱞﳲﳳﳴﹱﹷﹹﹻﹽﹿ‍",
        
        clusters: hashmap! {
                    "ﯪ" => "ئا",
                    "ﯫ" => "ئا",
                    "ﯬ" => "ئە",
                    "ﯭ" => "ئە",
                    "ﯮ" => "ئو",
                    "ﯯ" => "ئو",
                    "ﯰ" => "ئۇ",
                    "ﯱ" => "ئۇ",
                    "ﯲ" => "ئۆ",
                    "ﯳ" => "ئۆ",
                    "ﯴ" => "ئۈ",
                    "ﯵ" => "ئۈ",
                    "ﯶ" => "ئې",
                    "ﯷ" => "ئې",
                    "ﯸ" => "ئې",
                    "ﯹ" => "ئى",
                    "ﯺ" => "ئى",
                    "ﯻ" => "ئى",
                    "ﰃ" => "ئى",
                    "ﱨ" => "ئى",
                    "ﰀ" => "ئج",
                    "ﲗ" => "ئج",
                    "ﰁ" => "ئح",
                    "ﲘ" => "ئح",
                    "ﰂ" => "ئم",
                    "ﱦ" => "ئم",
                    "ﲚ" => "ئم",
                    "ﳟ" => "ئم",
                    "ﰄ" => "ئي",
                    "ﱩ" => "ئي",
                    "ﰅ" => "بج",
                    "ﲜ" => "بج",
                    "ﰆ" => "بح",
                    "ﲝ" => "بح",
                    "ﰇ" => "بخ",
                    "ﲞ" => "بخ",
                    "ﰈ" => "بم",
                    "ﱬ" => "بم",
                    "ﲟ" => "بم",
                    "ﳡ" => "بم",
                    "ﰉ" => "بى",
                    "ﱮ" => "بى",
                    "ﰊ" => "بي",
                    "ﱯ" => "بي",
                    "ﰋ" => "تج",
                    "ﲡ" => "تج",
                    "ﰌ" => "تح",
                    "ﲢ" => "تح",
                    "ﰍ" => "تخ",
                    "ﲣ" => "تخ",
                    "ﰎ" => "تم",
                    "ﱲ" => "تم",
                    "ﲤ" => "تم",
                    "ﳣ" => "تم",
                    "ﰏ" => "تى",
                    "ﱴ" => "تى",
                    "ﰐ" => "تي",
                    "ﱵ" => "تي",
                    "ﰑ" => "ثج",
                    "ﰒ" => "ثم",
                    "ﱸ" => "ثم",
                    "ﲦ" => "ثم",
                    "ﳥ" => "ثم",
                    "ﰓ" => "ثى",
                    "ﱺ" => "ثى",
                    "ﰔ" => "ثي",
                    "ﱻ" => "ثي",
                    "ﰕ" => "جح",
                    "ﲧ" => "جح",
                    "ﰖ" => "جم",
                    "ﲨ" => "جم",
                    "ﰗ" => "حج",
                    "ﲩ" => "حج",
                    "ﰘ" => "حم",
                    "ﲪ" => "حم",
                    "ﰙ" => "خج",
                    "ﲫ" => "خج",
                    "ﰚ" => "خح",
                    "ﰛ" => "خم",
                    "ﲬ" => "خم",
                    "ﰜ" => "سج",
                    "ﲭ" => "سج",
                    "ﴴ" => "سج",
                    "ﰝ" => "سح",
                    "ﲮ" => "سح",
                    "ﴵ" => "سح",
                    "ﰞ" => "سخ",
                    "ﲯ" => "سخ",
                    "ﴶ" => "سخ",
                    "ﰟ" => "سم",
                    "ﲰ" => "سم",
                    "ﳧ" => "سم",
                    "ﰠ" => "صح",
                    "ﲱ" => "صح",
                    "ﰡ" => "صم",
                    "ﲳ" => "صم",
                    "ﰢ" => "ضج",
                    "ﲴ" => "ضج",
                    "ﰣ" => "ضح",
                    "ﲵ" => "ضح",
                    "ﰤ" => "ضخ",
                    "ﲶ" => "ضخ",
                    "ﰥ" => "ضم",
                    "ﲷ" => "ضم",
                    "ﰦ" => "طح",
                    "ﲸ" => "طح",
                    "ﰧ" => "طم",
                    "ﴳ" => "طم",
                    "ﴺ" => "طم",
                    "ﰨ" => "ظم",
                    "ﲹ" => "ظم",
                    "ﴻ" => "ظم",
                    "ﰩ" => "عج",
                    "ﲺ" => "عج",
                    "ﰪ" => "عم",
                    "ﲻ" => "عم",
                    "ﰫ" => "غج",
                    "ﲼ" => "غج",
                    "ﰬ" => "غم",
                    "ﲽ" => "غم",
                    "ﰭ" => "فج",
                    "ﲾ" => "فج",
                    "ﰮ" => "فح",
                    "ﲿ" => "فح",
                    "ﰯ" => "فخ",
                    "ﳀ" => "فخ",
                    "ﰰ" => "فم",
                    "ﳁ" => "فم",
                    "ﰱ" => "فى",
                    "ﱼ" => "فى",
                    "ﰲ" => "في",
                    "ﱽ" => "في",
                    "ﰳ" => "قح",
                    "ﳂ" => "قح",
                    "ﰴ" => "قم",
                    "ﳃ" => "قم",
                    "ﰵ" => "قى",
                    "ﱾ" => "قى",
                    "ﰶ" => "قي",
                    "ﱿ" => "قي",
                    "ﰷ" => "كا",
                    "ﲀ" => "كا",
                    "ﰸ" => "كج",
                    "ﳄ" => "كج",
                    "ﰹ" => "كح",
                    "ﳅ" => "كح",
                    "ﰺ" => "كخ",
                    "ﳆ" => "كخ",
                    "ﰻ" => "كل",
                    "ﲁ" => "كل",
                    "ﳇ" => "كل",
                    "ﳫ" => "كل",
                    "ﰼ" => "كم",
                    "ﲂ" => "كم",
                    "ﳈ" => "كم",
                    "ﳬ" => "كم",
                    "ﰽ" => "كى",
                    "ﲃ" => "كى",
                    "ﰾ" => "كي",
                    "ﲄ" => "كي",
                    "ﰿ" => "لج",
                    "ﳉ" => "لج",
                    "ﱀ" => "لح",
                    "ﳊ" => "لح",
                    "ﱁ" => "لخ",
                    "ﳋ" => "لخ",
                    "ﱂ" => "لم",
                    "ﲅ" => "لم",
                    "ﳌ" => "لم",
                    "ﳭ" => "لم",
                    "ﱃ" => "لى",
                    "ﲆ" => "لى",
                    "ﱄ" => "لي",
                    "ﲇ" => "لي",
                    "ﱅ" => "مج",
                    "ﳎ" => "مج",
                    "ﱆ" => "مح",
                    "ﳏ" => "مح",
                    "ﱇ" => "مخ",
                    "ﳐ" => "مخ",
                    "ﱈ" => "مم",
                    "ﲉ" => "مم",
                    "ﳑ" => "مم",
                    "ﱉ" => "مى",
                    "ﱊ" => "مي",
                    "ﱋ" => "نج",
                    "ﳒ" => "نج",
                    "ﱌ" => "نح",
                    "ﳓ" => "نح",
                    "ﱍ" => "نخ",
                    "ﳔ" => "نخ",
                    "ﱎ" => "نم",
                    "ﲌ" => "نم",
                    "ﳕ" => "نم",
                    "ﳮ" => "نم",
                    "ﱏ" => "نى",
                    "ﲎ" => "نى",
                    "ﱐ" => "ني",
                    "ﲏ" => "ني",
                    "ﱑ" => "هج",
                    "ﳗ" => "هج",
                    "ﱒ" => "هم",
                    "ﳘ" => "هم",
                    "ﱓ" => "هى",
                    "ﱔ" => "هي",
                    "ﱕ" => "يج",
                    "ﳚ" => "يج",
                    "ﱖ" => "يح",
                    "ﳛ" => "يح",
                    "ﱗ" => "يخ",
                    "ﳜ" => "يخ",
                    "ﱘ" => "يم",
                    "ﲓ" => "يم",
                    "ﳝ" => "يم",
                    "ﳰ" => "يم",
                    "ﱙ" => "يى",
                    "ﲕ" => "يى",
                    "ﱚ" => "يي",
                    "ﲖ" => "يي",
                    "ﱛ" => "ذ",
                    "ﱜ" => "ر",
                    "ﱝ" => "ى",
                    "ﲐ" => "ى",
                    "ﱤ" => "ئر",
                    "ﱥ" => "ئز",
                    "ﱧ" => "ئن",
                    "ﱪ" => "بر",
                    "ﱫ" => "بز",
                    "ﱭ" => "بن",
                    "ﱰ" => "تر",
                    "ﱱ" => "تز",
                    "ﱳ" => "تن",
                    "ﱶ" => "ثر",
                    "ﱷ" => "ثز",
                    "ﱹ" => "ثن",
                    "ﲈ" => "ما",
                    "ﲊ" => "نر",
                    "ﲋ" => "نز",
                    "ﲍ" => "نن",
                    "ﲑ" => "ير",
                    "ﲒ" => "يز",
                    "ﲔ" => "ين",
                    "ﲙ" => "ئخ",
                    "ﲛ" => "ئه",
                    "ﳠ" => "ئه",
                    "ﲠ" => "به",
                    "ﳢ" => "به",
                    "ﲥ" => "ته",
                    "ﳤ" => "ته",
                    "ﲲ" => "صخ",
                    "ﳍ" => "له",
                    "ﳖ" => "نه",
                    "ﳯ" => "نه",
                    "ﳙ" => "ه",
                    "ﳞ" => "يه",
                    "ﳱ" => "يه",
                    "ﳦ" => "ثه",
                    "ﳨ" => "سه",
                    "ﴱ" => "سه",
                    "ﳩ" => "شم",
                    "ﴌ" => "شم",
                    "ﴨ" => "شم",
                    "ﴰ" => "شم",
                    "ﳪ" => "شه",
                    "ﴲ" => "شه",
                    "ﳵ" => "طى",
                    "ﴑ" => "طى",
                    "ﳶ" => "طي",
                    "ﴒ" => "طي",
                    "ﳷ" => "عى",
                    "ﴓ" => "عى",
                    "ﳸ" => "عي",
                    "ﴔ" => "عي",
                    "ﳹ" => "غى",
                    "ﴕ" => "غى",
                    "ﳺ" => "غي",
                    "ﴖ" => "غي",
                    "ﳻ" => "سى",
                    "ﴗ" => "سى",
                    "ﳼ" => "سي",
                    "ﴘ" => "سي",
                    "ﳽ" => "شى",
                    "ﴙ" => "شى",
                    "ﳾ" => "شي",
                    "ﴚ" => "شي",
                    "ﳿ" => "حى",
                    "ﴛ" => "حى",
                    "ﴀ" => "حي",
                    "ﴜ" => "حي",
                    "ﴁ" => "جى",
                    "ﴝ" => "جى",
                    "ﴂ" => "جي",
                    "ﴞ" => "جي",
                    "ﴃ" => "خى",
                    "ﴟ" => "خى",
                    "ﴄ" => "خي",
                    "ﴠ" => "خي",
                    "ﴅ" => "صى",
                    "ﴡ" => "صى",
                    "ﴆ" => "صي",
                    "ﴢ" => "صي",
                    "ﴇ" => "ضى",
                    "ﴣ" => "ضى",
                    "ﴈ" => "ضي",
                    "ﴤ" => "ضي",
                    "ﴉ" => "شج",
                    "ﴥ" => "شج",
                    "ﴭ" => "شج",
                    "ﴷ" => "شج",
                    "ﴊ" => "شح",
                    "ﴦ" => "شح",
                    "ﴮ" => "شح",
                    "ﴸ" => "شح",
                    "ﴋ" => "شخ",
                    "ﴧ" => "شخ",
                    "ﴯ" => "شخ",
                    "ﴹ" => "شخ",
                    "ﴍ" => "شر",
                    "ﴩ" => "شر",
                    "ﴎ" => "سر",
                    "ﴪ" => "سر",
                    "ﴏ" => "صر",
                    "ﴫ" => "صر",
                    "ﴐ" => "ضر",
                    "ﴬ" => "ضر",
                    "ﵐ" => "تجم",
                    "ﵑ" => "تحج",
                    "ﵒ" => "تحج",
                    "ﵓ" => "تحم",
                    "ﵔ" => "تخم",
                    "ﵕ" => "تمج",
                    "ﵖ" => "تمح",
                    "ﵗ" => "تمخ",
                    "ﵘ" =>   "جمح",
                    "ﵙ" => "جمح",
                    "ﵚ" => "حمي",
                    "ﵛ" => "حمى",
                    "ﵜ" => "سحج",
                    "ﵝ" => "سجح",
                    "ﵞ" => "سجى",
                    "ﵟ" => "سمح",
                    "ﵠ" => "سمح",
                    "ﵡ" => "سمج",
                    "ﵢ" => "سمم",
                    "ﵣ" => "سمم",
                    "ﵤ" => "صحح",
                    "ﵥ" => "صحح",
                    "ﵦ" => "صمم",
                    "ﷅ" => "صمم",
                    "ﵧ" => "شحم",
                    "ﵨ" => "شحم",
                    "ﵩ" => "شجي",
                    "ﵪ" => "شمخ",
                    "ﵫ" => "شمخ",
                    "ﵬ" => "شمم",
                    "ﵭ" => "شمم",
                    "ﵮ" => "ضحى",
                    "ﵯ" => "ضخم",
                    "ﵰ" => "ضخم",
                    "ﵱ" => "طمح",
                    "ﵲ" => "طمح",
                    "ﵳ" => "طمم",
                    "ﵴ" => "طمي",
                    "ﵵ" => "عجم",
                    "ﷄ" => "عجم",
                    "ﵶ" => "عمم",
                    "ﵷ" => "عمم",
                    "ﵸ" => "عمى",
                    "ﵹ" => "غمم",
                    "ﵺ" => "غمي",
                    "ﵻ" => "غمى",
                    "ﵼ" => "فخم",
                    "ﵽ" => "فخم",
                    "ﵾ" => "قمح",
                    "ﶴ" => "قمح",
                    "ﵿ" => "قمم",
                    "ﶀ" => "لحم",
                    "ﶵ" => "لحم",
                    "ﶁ" => "لحي",
                    "ﶂ" => "لحى",
                    "ﶃ" => "لجج",
                    "ﶄ" => "لجج",
                    "ﶅ" => "لخم",
                    "ﶆ" => "لخم",
                    "ﶇ" => "لمح",
                    "ﶈ" => "لمح",
                    "ﶉ" => "محج",
                    "ﶊ" => "محم",
                    "ﶋ" => "محي",
                    "ﶌ" => "مجح",
                    "ﶍ" => "مجم",
                    "ﶎ" => "مخج",
                    "ﶏ" => "مخم",
                    "ﶒ" => "مجخ",
                    "ﶓ" => "همج",
                    "ﶔ" => "همم",
                    "ﶕ" => "نحم",
                    "ﶖ" => "نحى",
                    "ﶗ" => "نجم",
                    "ﶘ" => "نجم",
                    "ﶙ" => "نجى",
                    "ﶚ" => "نمي",
                    "ﶛ" => "نمى",
                    "ﶜ" => "يمم",
                    "ﶝ" => "يمم",
                    "ﶞ" => "بخي",
                    "ﶟ" => "تجي",
                    "ﶠ" => "تجى",
                    "ﶡ" => "تخي",
                    "ﶢ" => "تخى",
                    "ﶣ" => "تمي",
                    "ﶤ" => "تمى",
                    "ﶥ" => "جمي",
                    "ﶦ" => "جحى",
                    "ﶧ" => "جمى",
                    "ﶨ" => "سخى",
                    "ﶩ" => "صحي",
                    "ﶪ" => "شحي",
                    "ﶫ" => "ضحي",
                    "ﶬ" => "لجي",
                    "ﶭ" => "لمي",
                    "ﶮ" => "يحي",
                    "ﶯ" => "يجي",
                    "ﶰ" => "يمي",
                    "ﶱ" => "ممي",
                    "ﶲ" => "قمي",
                    "ﶳ" => "نحي",
                    "ﶶ" => "عمي",
                    "ﶷ" => "كمي",
                    "ﶸ" => "نجح",
                    "ﶽ" => "نجح",
                    "ﶹ" => "مخي",
                    "ﶺ" => "لجم",
                    "ﶼ" => "لجم",
                    "ﶻ" => "كمم",
                    "ﷃ" => "كمم",
                    "ﶾ" => "جحي",
                    "ﶿ" => "حجي",
                    "ﷀ" => "مجي",
                    "ﷁ" => "فمي",
                    "ﷂ" => "بحي",
                    "ﷆ" => "سخي",
                    "ﷇ" => "نجي",
                    "ﻵ" => "لآ",
                    "ﻶ" => "لآ",
                    "ﻷ" => "لأ",
                    "ﻸ" => "لأ",
                    "ﻹ" => "لإ",
                    "ﻺ" => "لإ",
                    "ﻻ" => "لا",
                    "ﻼ" => "لا",
                    "ﷺ" => "صلى الله عليه وسلم",
                    "﷽" => "بسم الله الرحمن الرحيم",
                    "ﷲ" => "الله",
                    "ﷳ" => "أكبر",
                    "ﷴ" => "محمد",
                    "ﷶ" => "رسول",
                    "ﷷ" => "عليه",
                    "ﷸ" => "وسلم",
                    "ﷹ" => "صلى",
                    "﷼" => "ریال",
                    "ﷻ" => "جل جلاله",
                    "ﷱ" => "قلے",
                    "ﷰ" => "صلے",
                    "ﷵ" => "صلعم",
        }
    }
}

fn main() -> Result<()> {

    let mut fname = String::new();
    let mut normalise = false;
    let mut tokenise = false;
    let mut uniq = false;
    let mut version = false;

    {
        let mut parser = ArgumentParser::new();
        parser.set_description("convert arabic script into archigraphemes. Input must contain only alphabetic Arabic script. Use --tok if that is not the case.");

        //FIXME add optionality stdin/file add stdout ; check clap: rust crate
        parser.refer(&mut fname)
                    .add_option(&["--infile"], Store,
                    "input text");

        //FIXME quitar normalise y tokenise !! que se hagan siempre
        parser.refer(&mut normalise)
                    .add_option(&["-n", "--norm"], StoreTrue,
                    "normalise clusters of Arabic Presentation Forms (FB50–FDFF, FE70–FEFF)");
        parser.refer(&mut tokenise)
                    .add_option(&["-t", "--tok"], StoreTrue,
                    "tokenise before conversion (necessary if stream is NOT yet tokenised");

        parser.refer(&mut uniq)
                    .add_option(&["-u", "--uniq"], StoreTrue,
                    "output each unique archigraphemic letterblock, number of total occurrences and list of unique occurrences");
        
        parser.refer(&mut version)
                    .add_option(&["--version"], StoreTrue,
                    "prints the program version number and exits successfully");
        parser.parse_args_or_exit();
    }

    if version {
        println!("rasm 1.0");
        process::exit(0);
    }

    /*
     * load data
     */

    let chars = load_arabic_inventory();
    let mappings = load_rasm_mappings(&chars);

    /*
     * compile regexes
     */

    let re_norm = Regex::new(&chars.clusters.keys().map(|s| &**s).collect::<Vec<_>>().join("|")).unwrap(); //FIXME <Vec<_>> ??

    let re_ara = Regex::new(&format!("[^{A}{N}{Y}{B}{G}{R}{D}{T}{C}{S}{Q}{F}{E}{W}{H}{M}{L}{K}{diac} ]",
                            A=chars.A, N=chars.N, Y=chars.Y, B=chars.B, G=chars.G, R=chars.R, D=chars.D,
                            T=chars.T, C=chars.C, S=chars.S, Q=chars.Q, F=chars.F, E=chars.E, W=chars.W,
                            H=chars.H, M=chars.M, L=chars.L, K=chars.K, diac=chars.diac)).unwrap();

    let re_clean = Regex::new(&format!("[{}]", chars.diac)).unwrap();

    let re_rasm_end = Regex::new(&format!("({})$", mappings.mapping_end.keys().map(|s| &**s).collect::<Vec<_>>().join("|")) ).unwrap();

    let re_rasm_gen = Regex::new(&mappings.mapping_gen.keys().map(|s| &**s).collect::<Vec<_>>().join("|")).unwrap();
    let re_rasm_ara = Regex::new(&mappings.mapping_ara.keys().map(|s| &**s).collect::<Vec<_>>().join("|")).unwrap();


    /*
     * prepare containers to index data
     */

    //FIXME add arg check for uniq
    let mut letterblock_ara = HashMap::new();
    //let mut letterblock_count = HashMap::new();
    //let mut letterblock_tokens = HashMap::new();

    /*
     * process file
     */

    let fp = File::open(fname)?;

    for line in  BufReader::new(fp).lines() {
        let line_read = line.unwrap();
        
        /* normalise */

        let line_norm = re_norm.replace_all(&line_read, |cap: &Captures| {
            chars.clusters.get(cap.get(0).unwrap().as_str()).unwrap()
        });

        /* tokenise */

        let line_clean = re_ara.replace_all(&line_norm, " ");

        for tok in line_clean.split_whitespace() {

            let tok_clean = re_clean.replace_all(&tok, "");

            /* reduce */

            let tok_reduced_lat = re_rasm_end.replace_all(&tok_clean, |cap: &Captures| {
                mappings.mapping_end.get(cap.get(0).unwrap().as_str()).unwrap()
            });

            let tok_reduced_lat = re_rasm_gen.replace_all(&tok_reduced_lat, |cap: &Captures| {
                mappings.mapping_gen.get(cap.get(0).unwrap().as_str()).unwrap()
            });

            let tok_reduced_ara = re_rasm_ara.replace_all(&tok_reduced_lat, |cap: &Captures| {
                mappings.mapping_ara.get(cap.get(0).unwrap().as_str()).unwrap()
            });

            /*
             * normal output
             */

            println!("{}\t{}\t{}", tok_clean, tok_reduced_lat, tok_reduced_ara); //DEBUG  الله A LLH   ا لله

            /*
             * uniq output
             */

            //FIXME add arg check for uniq
            for zipped in tok_reduced_lat.split_whitespace().zip(tok_reduced_ara.split_whitespace()) {
                //let (letterblock_lat, letterblock_ara) = zipped; //FIXME
                let letterblock_lat = zipped.0.to_string(); ///////////////////////////
                let letterblock_ara = zipped.1.to_string(); ///////////////////////////

                //println!("{}", zipped); //DEBUG

                //println!("{} {}", letterblock_lat, letterblock_ara); //DEBUG

                letterblock_ara.insert(letterblock_lat.to_string(), letterblock_ara.to_string());
                //letterblock_count.insert(letterblock_lat, 0);  //FIXME

                //let count = map.entry(key).get().unwrap_or_else(|v| v.insert(0));
                // *count += 1;

                //letterblock_tokens.insert(letterblock_lat, []); //FIXME
                
            }
        }
    }

    //TODO vamos a considerar que normalise, tokenise y reduce son obligatorios, se hacen siempre
    // junta los resultados en una estructura
    // opcionalmente, segun el usuario llame al comando con uniq, hacer ese procesado.

    Ok(())
}
