#!/bin/sh
wget -t 1 -T 5 "http://humour-blague.com/blagues-2/index.php#" -O- 2>/dev/null | sed -e '1,/                        <p align="left" class="blague">/ d' -e '/                        <p align="left" class="blague">&nbsp;<\/p>/,$ d' 2>/dev/null | html2text | sed -e 's/&quot;/"/g' -e 's/&amp;/\&/g'
