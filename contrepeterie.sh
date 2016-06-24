#!/bin/bash
wget -t 1 -T 5 "http://www.contrepeterie.net/home$(( RANDOM % 8 + 1)).htm" -O- 2>/dev/null | sed -e '1,/  <tbody>/ d' -e '/  <\/tbody>/,$ d' 2>/dev/null | html2text | sed -e 's/^ *//; s/ *$//; /^$/d' -e 's/&quot;/"/g' -e 's/&amp;/\&/g' | sort -R | head -n 1
