# -*- coding: utf-8 -*-
from __future__ import division
import scrapy
import sys
import json
import base64, zlib
import scrapy
import re

class Parsers:
	def rel2url(self, url, rel):
		import urlparse
		r = urlparse.urljoin(response.url, '/') + rel
		return r

	def CTFTIME_parse_event_list_past_list2event_urls(self, response, url):
		# https://ctftime.org/event/list/past
		# CTf Events 목록 페이지.
		# to 개별 cTF 정보 페이지 urls.
		if url != 'https://ctftime.org/event/list/past':
			return None
		###
		selector = scrapy.Selector(text=response)
		r = selector.xpath(r'/html/body/div[2]/table/tr[4]/td[1]/a/@href').extract()
		urls = [self.rel2url(url, rel) for rel in r]
		return urls

	def CTFTIME_parse_event_page2infos(self, response, url):
		# https://ctftime.org/event/???
		# ex) https://ctftime.org/event/340
		# 개별 CTF 정보 페이지.
		# to Description, Prizes, Event Task page
		if re.match(r'https://ctftime.org/event/\d+', url) == None:
			return None
		###
		selector = scrapy.Selector(text=response)
		desc = selector.xpath('/html/body/div[2]/div[3]').extract()[0]
		prizes = selector.xpath('/html/body/div[2]/div[4]').extract()[0]
		event_task_page = selector.xpath('/html/body/div[2]/div[5]/div[1]/p/a/@href').extract()[0]
		event_task_page = self.rel2url(url, event_task_page)
		ret = {'desc': desc, 'prizes': prizes, 'event_task_page': event_task_page}
		return ret

	def CTFTIME_parse_event_tasks2tasks_info(self, response, url):
		# https://ctftime.org/event/???/tasks/
		# ex) https://ctftime.org/event/340/tasks/
		# 각 CTF 하나의 문제 목록.
		# to [{'url': ~, 'point': ~, 'tags': ~, 'taskpage': ~}, ...]
		if re.match(r'https://ctftime.org/event/\d+/tasks/', url) == None:
			return None
		###
		selector = scrapy.Selector(text=response)
		ret = []
		probs = selector.xpath('/html/body/div[2]/table/tr')
		for one in probs[1:]: # 0 is table header.
			name = one.xpath('.//td[1]/a/text()').extract()[0]
			point = one.xpath('.//td[2]/text()').extract()[0]
			tags = one.xpath('.//td[3]/text()').extract()[0]
			writeups_link = one.xpath('.//td[1]/a/@href').extract()[0]
			o = {'name': name, 'point': point, 'tags': tags, 'taskpage': writeups_link}
			ret.append(o)
		return ret

	def CTFITME_parse_task2info(self, response, url):
		# https://ctftime.org/task/????
		# ex) https://ctftime.org/task/2566
		# 문제 하나 풀이 페이지.
		# to {'name': ~, point': ~, 'tags': ~, 'desc': ~, 'writeup_links': [~, ~, ...]}
		if re.match(r'https://ctftime.org/task/\d+', url) == None:
			return None
		###
		selector = scrapy.Selector(text=response)
		ret = {}
		name = selector.xpath('/html/body/div[2]/div[1]/h2/text()').extract()[0]
		point = selector.xpath('/html/body/div[2]/div[2]/div[1]/p[1]/text()').extract()[0]
		tags = selector.xpath("/html/body/div[2]/div[2]/div[1]/p[2]/span[contains(concat(' ', normalize-space(@class), ' '), ' label-info ')]/text()").extract()
		desc = selector.xpath('/html/body/div[2]/div[3]').extract()[0]
		links = []
		for link in selector.xpath('/html/body/div[2]/table/tr[2]/td[1]/a/@href'):
			links.append(link.extract())
		ret['name'] = name
		ret['point'] = point
		ret['tags'] = tags
		ret['desc'] = desc
		ret['writeup_links'] = links
		return ret

	def CTFTIME_parse_writeup2Info(self, response, url):
		# https://ctftime.org/writeup/????
		# ex) https://ctftime.org/writeup/3625
		# task writeup 하나. 
		# to {'prob_name': ~, 'tags': ~, 'desc': ~, 'origin_writeup': ~, 'ctf_name': ~}
		if re.match(r'https://ctftime.org/writeup/\d+', url) == None:
			return None
		###
		selector = scrapy.Selector(text=response)
		ret = {}
		ret['prob_name'] = selector.xpath('/html/body/div[2]/div[1]/h2/text()').extract()[0]
		ret['tags'] = selector.xpath("/html/body/div[2]/p[1]/span[contains(concat(' ', normalize-space(@class), ' '), ' label-info ')]/text()").extract()
		ret['desc'] = selector.xpath('/html/body/div[2]/div[2]').extract()
		ret['origin_writeup'] = selector.xpath('/html/body/div[2]/div[3]').extract()
		if len(ret['origin_writeup']) > 0:
			ret['origin_writeup'] = ret['origin_writeup'][0]
		else:
			ret['origin_writeup'] = ''
		ret['ctf_name'] = selector.xpath('/html/body/div[2]/ul/li[3]/a/text()').extract()[0]
		return ret


class GITHUB_ITER:
	def __init__(self, initdir):
		self.initdir = initdir

	def __iter__(self):
		# Directory Structure : CTF이름/문제분류/문제이름/...
		# to {'ctf_name': ~, 'category': ~, 'prob_name': ~}
		import glob, re, os
		cwd = os.getcwd()
		os.chdir(self.initdir)
		globed = glob.glob('./*/*/*/**')
		globed = [x for x in globed if os.path.isfile(x)]
		for x in globed:
			ctf_name, prob_category, prob_name, entry_name = re.findall(r'\.\\(.*?)\\(.*?)\\(.*?)\\(.*)', x)[0]
			#print ctf_name, prob_category, prob_name, entry_name
			with open(x, 'rb') as f:
				yield {'ctf_name': ctf_name, 'tags': [prob_category], 'prob_name': prob_name, 'url': entry_name, 'body': f.read(), 'src_url': 'GITHUB', 'src_type': 'GITHUB'}
		os.chdir(cwd)

def simple_count_search(keywords, iterable, field):
	if type(keywords) == str:
		keywords = keywords.split(' ')
	counted = []
	for i, data in enumerate(iterable):
		count = 0 
		for keyword in keywords:
			count += data[field].count(keyword)
		counted.append(count)
	counted = [(i[0], i[1]) for i in sorted(enumerate(counted), key=lambda x:x[1], reverse=True)]
	# return list of (index, countnum)
	return counted[:30]

def search_dictionary(list_of_dic, k, v):
	for dic in list_of_dic:
		if dic[k] == v:
			yield dic

'''
NOT WORKING! 
def check_filetype(bin):
	import sys
	###
	# set PATH=D:\ctf\file-5.03-bin\bin;D:\ctf\file-5.03-bin\share\misc;D:\ctf\file-5.03-dep\bin;%PATH%
	l = [r'D:\ctf\file-5.03-bin\bin', r'D:\ctf\file-5.03-dep\bin', r'D:\ctf\file-5.03-bin\share\misc']
	for x in l:
		if x not in sys.path:
			sys.path.append(x)
	###
	import magic
	m = Magic(magic_file=r'D:\ctf\file-5.03-bin\share\misc\magic')
	return m.from_buffer(bin)
	###
'''


import string 

def istext(s):
	# source : http://stackoverflow.com/questions/1446549/how-to-identify-binary-and-text-files-using-python
	#s=open(filename).read(512)
	s = s[:512]
	text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
	_null_trans = string.maketrans("", "")
	if not s:
		# Empty files are considered text
		return True
	if "\0" in s:
		# Files with null bytes are likely binary
		return False
	# Get the non-text characters (maps a character to itself then
	# use the 'remove' option to get rid of the text characters.)
	t = s.translate(_null_trans, text_characters)
	# If more than 30% non-text characters, then
	# this is considered a binary file
	if float(len(t))/float(len(s)) > 0.30:
		return False
	return True

from readability.readability import Document

def extract_contents(html):
	if istext(html) == True:
		try:
			d = Document(html).summary()
			return (True, d)
		except:
			return (False, html)
	else:
		return (False, html)

import html2text

def extract_contents2txt(html):
	is_text, html = extract_contents(html)
	if is_text == False:
		return None
	print type(html)
	try:
		text = html2text.html2text(html)
		return text
	except:
		return None

def add_writeuppage_info_one(x):
	# add basic parse info
	print 'adding writeup page parsing info...'
	p = Parsers()
	a = p.CTFTIME_parse_writeup2Info(x['body'], x['url'])
	if a != None:
		x.update(a)
	# add extracted contents
	print 'adding extracted contents...'
	x['contents'] = extract_contents2txt(x['body'])
	# add text analytics
	# NOT AVAILABLE (YET)

def add_writeuppage_info(filename):
	with open(filename, 'rb') as infile:
		data = []
		# first, load data.
		for line in infile:
			d = json.loads(line)
			d['body'] = zlib.decompress(base64.b64decode(d['body']))
			data.append(d)
		for x in data:
			add_writeuppage_info_one(x)
	return data

def add_writeuppage_info_2file(filename, outfilename):
	with open(filename, 'rU') as infile:
		with open(outfilename, 'w') as outf:
			data = []
			# first, load data.
			i = 0
			for line in infile:
				i += 1
				#if i <= 6730:
				#	continue
				print len(line), i
				d = json.loads(line)
				d['body'] = zlib.decompress(base64.b64decode(d['body']))
				add_writeuppage_info_one(d)
				d['body'] = base64.b64encode(zlib.compress(d['body']))
				outf.write(json.dumps(d) + '\n')
				

def load_json(fn, n=1000000000000000000000):
	### load json data (crawled data)
	data = []
	with open(fn, 'r') as infile:
		i = 0
		for line in infile:
			if i >= n:
				break
			i += 1
			d = json.loads(line)
			d['body'] = zlib.decompress(base64.b64decode(d['body']))
			data.append(d)
	#######
	return data

def search(data, keywords):
	p = Parsers()
	# github 페이지, src가 github인 페이지, ctftime writeup 페이지, src가 ctftime writeup페이지인 페이지만 검색. 
	# ctftime.org 정보 추가. 
	search_targets = [x for x in data if (('ctftime.org/writeup/' in x['src_url']) and (not 'https://ctftime.org' in x['url'])) or ('ctftime.org/writeup/' in x['url'])]	# search ctftime
	# github 정보 추가. 
	search_targets += GITHUB_ITER(r'D:\ctf\data\write-ups-2016')
	# search
	s = simple_count_search(keywords, search_targets, 'body')
	for cand in s:
		# cand : (index, match count)
		req_entry = search_targets[cand[0]]
		body = req_entry['body']
		url = req_entry['url']
		# if this is not from github
		src_req_entry = None
		if 'src_type' not in req_entry or req_entry['src_type'] != 'GITHUB':
			info = p.CTFTIME_parse_writeup2Info(body, url)
			# if this page is not writeup page
			if info == None:
				src_req_entry = search_dictionary(search_targets, 'url', req_entry['src_url']).next()
				assert src_req_entry != None
				src_req_entry.update(p.CTFTIME_parse_writeup2Info(src_req_entry['body'], src_req_entry['url']))
			else:
				req_entry.update(info)
		elif req_entry['src_type'] == 'GITHUB':
			src_req_entry = search_dictionary(search_targets, 'url', req_entry['src_url']).next()
		yield (req_entry, src_req_entry)


def search_preprocessed(data, keywords):
	p = Parsers()
	# github 페이지, src가 github인 페이지, ctftime writeup 페이지, src가 ctftime writeup페이지인 페이지만 검색. 
	# ctftime.org 정보 추가. 
	search_targets = [x for x in data if (('ctftime.org/writeup/' in x['src_url']) and (not 'https://ctftime.org' in x['url'])) or ('ctftime.org/writeup/' in x['url'])]	# search ctftime
	# github 정보 추가. 
	search_targets += GITHUB_ITER(r'D:\ctf\data\write-ups-2016')
	# search
	s = simple_count_search(keywords, search_targets, 'body')
	for cand in s:
		# cand : (index, match count)
		req_entry = search_targets[cand[0]]
		# if this is not from github
		src_req_entry = None
		if 'src_type' not in req_entry or req_entry['src_type'] != 'GITHUB':
			# if this page is not writeup page
			if not 'tags' in req_entry:
				src_req_entry = search_dictionary(search_targets, 'url', req_entry['src_url']).next()
		elif req_entry['src_type'] == 'GITHUB':
			src_req_entry = search_dictionary(search_targets, 'url', req_entry['src_url']).next()
		yield (req_entry, src_req_entry)


if __name__ == '__main__': 
	if sys.argv[1] == 'search':
		data = load_json('general.jsonline')
		keywords = sys.argv[2]
		for x, src in search(data, keywords):
			tags = x['tags'] if src == None else src['tags']
			print tags, x['url']
	elif sys.argv[1] == 'search_preprocess':
		data = load_json('pre_processed.jsonline', 1000)
		keywords = sys.argv[2]
		for x, src in search_preprocessed(data, keywords):
			tags = x['tags'] if src == None else src['tags']
			print tags, x['url'], src['url']
	elif sys.argv[1] == 'preprocess':
		add_writeuppage_info_2file('general.jsonline', 'pre_processed.jsonline')
	elif sys.argv[1] == 'update':
		# update github
		
		pass
	elif sys.argv[1] == 'update_preprocess':
		pass
	else:
		print 'unsupported method'
