#-*- coding: utf-8 -*-
# coding: utf-8
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
import os
import re
from settings import DATA_DIR

RE = re.compile


url_parsers = [ RE(

#  Based on RFC 1738 predefined HTTP schema
#  http://www.ietf.org/rfc/rfc1738.txt

# lowalpha       = "a" | "b" ... | "y" | "z"
# hialpha        = "A" | "B" ... | "Y" | "Z"
# digit          = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
# digits         = 1*digit
# alpha          = lowalpha | hialpha
# hex            = digit | "A" | "B" | "C" | "D" | "E" | "F" | "a" | "b" | "c" | "d" | "e" | "f"
# alphadigit     = alpha | digit

# safe           = "$" | "-" | "_" | "." | "+"
# extra          = "!" | "*" | "'" | "(" | ")" | ","

# uchar          = unreserved | escape
# unreserved     = alpha | digit | safe | extra
# escape         = "%" hex hex

# search         = *[ uchar | ";" | ":" | "@" | "&" | "=" ]

# hsegment       = *[ uchar | ";" | ":" | "@" | "&" | "=" ]
# hpath          = hsegment *[ "/" hsegment ]

# domainlabel    = alphadigit | alphadigit *[ alphadigit | "-" ] alphadigit
# toplabel       = alpha | alpha *[ alphadigit | "-" ] alphadigit
# hostname       = *[ domainlabel "." ] toplabel
# hostnumber     = digits "." digits "." digits "." digits
# host           = hostname | hostnumber
# port           = digits
# hostport       = host [ ":" port ]

# httpurl        = "http://" hostport [ "/" hpath [ "?" search ]]

# Should we support login for http? (login = [ user [ ":" password ] "@" ] hostport ]])

    ur"""
    (             # first group: whole url
        https?://   # schema
        (           # one more group for re.findall not to flatten list
            (?:
                (?:
                    (?:\w | (\w[\w-]*\w))
                    \.                     # Dot
                )+                         # Domainlabel, * in RFC
                (?:
                     # still no posix character classes :C http://bugs.python.org/issue2636
                    [a-zа-я]{2,}
                )                     # Toplabel, same as domainlabel in RFC
            )                         # hostname
            |                         # or
            (?: \d+\.\d+\.\d+\.\d+ )  # hostnumber
        )
        (?:
            :[0-9]+
        )?    # Port
        (?:
            /                           # Slash
            (?:
                (?:
                    [-\w$.+()!*',;:@&=]
                    | %[0-9a-f][0-9a-f]    # escapes
                )*                         # First path component
                (?:
                    /                      # Slash
                    (?:
                        [-\w$.+()!*',;:@&=]
                        | %[0-9a-f][0-9a-f]   # escapes
                    )*
                )*                         # extra path components
            )                           #  Path
            (?:
                \?                  # question mark
                (?:
                    [-\w$.+()!*',;:@&=]
                    | [/]                #  Not in RFC
                    | %[0-9a-f][0-9a-f]  # escapes
                )*
            )?                     # Search
            (?:
                \#                 # hash
                (?:
                    [-\w$.+()!*',;:@&=]
                    | [/]                 # allowing slash in fragments
                    | %[0-9a-f][0-9a-f]   # escapes
                )*
            )?                           # Fragment
        )?                               # [ "/" path [ "?" search [ "#" fragment ] ] ]
        (?<!          # Look-behind
            [.,!?( ]                   # Let's not end with this
        )
    )
    """, re.UNICODE | re.VERBOSE | re.IGNORECASE),
    #RE(ur'\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))'),
    RE(ur'https?://[^\s<>"]+|www\.[^\s<>"]+'),
    RE(ur'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
    RE(ur'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'),
    RE(ur'(https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})'),
    #RE(ur'((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?')
    ]

def custom_md_url_parser(data):
	result_urls = []
	pr = ''
	i = 0
	while i < xrange(len(data)):
		HTTP = 'http://'
		HTTPS = 'https://'

# tp://nusgreyhats.org/write-ups/32C3-CTF-Flash
# http://kchung.co/lol.py').read()
def parse_md_url(data):
	exp = r'\[([^\]\[]+)\]\((' + r'[^\)\(\r\n]*(?:\([^\)\r\n]*\))?[^\)\r\n]*' + r')[\)\r\n]'
	result = [x for x in re.findall(exp, data) if x[1].startswith('http://') or x[1].startswith('https://')]
	data = re.sub(exp, '', data)
	result2 = [x for x in re.findall(r'''(https?://.*?)[ \r\n\>\]]''', data)]
	result3 = []
	for x in result2:
		while 1:
			if x[-1] in ('`', '"', ',', '.', "'", ']', ';', '*', '}'):
				x = x[:-1]
			elif x[-1] == ')' and x.count('(') == 1 and x.count(')') == 1:
				break
			elif x[-1] == ')' and x.count('(') > 1:
				assert 0
			elif x[-1] == ')' and x.count(')') > 1 and x.count('(') < 2:
				x = x[:x.find(')')]
			elif x[-1] == ')':
				x = x[:-1]
			else:
				break
				
		result3.append(('', x))
	result += result3
	return result


import fnmatch
import os
import json

matches = []
for root, dirnames, filenames in os.walk('data'):
    for filename in fnmatch.filter(filenames, '*.md'):
        matches.append(os.path.join(root, filename))

scraped = []
import urllib2
for md_file in matches:
	md_filebuf = open(md_file,'rb').read()
	for label, url in parse_md_url(md_filebuf):
		a = {}
		a['src_url'] = md_file
		a['url'] = url
		a['label'] = label
		scraped.append(a)

open(os.path.sep.join([DATA_DIR, 'scrapy', 'urls_to_crawl.json']), 'wb').write(json.dumps(scraped))


