# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
import re
import json
from scrapy.selector import Selector
import base64, zlib
from scrapy.utils import request
from scrapy.crawler import CrawlerProcess
from scrapy.conf import settings
import os

class GeneralSpider(scrapy.Spider):
	name = "General"
	#allowed_domains = ["domain.com"]
	start_urls = (
		'https://ctftime.org/event/list/past',
	)

	link_re = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
	le = LinkExtractor(tags=('a', 'img', 'embed', 'link', 'script',), attrs=('src', 'href',), deny_extensions=[])

	def extract_urls(self, response):
		urls = set()
		### NOT WORKING! NOT USE! 
		'''for x in self.link_re.findall(response.body):
			print '!'
			x = x[0]
			for y in ["'", '"', '>', '<', ')', '(', '`', '\\']:
				if y in x:
					x = x[:x.index(y)]
			if (not 'http://' in x) or (not 'https://' in x):
				continue
			urls.add(x)'''
		if hasattr(response, 'text'):
			for url in self.le.extract_links(response):
				urls.add(url)
		return list(urls)


	def parse_items(self, response):
		from Project.items import ProjectItem
		item = ProjectItem()
		item['src_url'] = response.meta['src_url'] if 'src_url' in response.meta else ''
		item['url'] = response.url
		item['label'] = ''
		item['body'] = base64.b64encode(zlib.compress(response.body, 9))
		item['encoding'] = response.encoding if hasattr(response, 'encoding') else ''
		return item

	
	def blacklist_url(self, url):
		# return True : blacklisted
		# return False : not blacklisted
		if ('ctftime.org/team/' in url) or ('ctftime.org/user' in url) or ('ctftime.org/login' in url) or ('/edit/' in url) or ('/task/' in url and '/writeup/' in url) or ('/task' in url and '/new/' in url):
			return True
		else:
			return False

	###### PARSE FUNCTION OPTIONS

	DEPTH = None
	crawl_resources = True
	def filter_func(self, url):
		if 'https://ctftime.org/event' in url or 'https://ctftime.org/task/' in url:
			return True
		else:
			return False
	DEPTH_OUTOF = 1 # -1 means disabled
	### 

	def parse(self, response):
		# OPTION : depth, crawl_resources, filter_func
		# depth(int) : maximum depth of crawl
		# crawl_resources(bool) : whether to crawl resources that needed to render the crawled page.
		# filter_func(function(url: string)) : a filter function to filter by url.
		# depth_outof(int) : how much depth is crawled outof allowed pages. 
		# * depth and filter_func cannot be used concurrently!
		###########################
		### DEBUG CODE
		with open(os.path.sep.join([settings['DATA_DIR'], 'scrapy', 'did2.txt']), 'a') as f:
			f.write(str(response.url) + '\t' + (response.meta['src_url'] if 'src_url' in response.meta else '') + '\n')
		###
		if self.DEPTH != None and self.filter_func != None:
			print 'self.DEPTH != None and self.filter_func != None'
			exit()
		assert self.crawl_resources in (True, False)
		### Yield Items 
		yield self.parse_items(response)
		###
		### Yield New Requests
		depth = response.meta['depth'] if 'depth' in response.meta else 0
		depth_outof = response.meta['depth_outof'] if 'depth_outof' in response.meta else -1
		if self.DEPTH_OUTOF == depth_outof and depth >= self.DEPTH:
			return
		urls = [x.url for x in self.extract_urls(response) if self.blacklist_url(x.url) == False]
		urls2 = [] 
		if self.filter_func != None:
			for x in urls:
				if self.filter_func(x) == True and depth_outof == -1:
					urls2.append((x, -1))
				else:
					if self.DEPTH_OUTOF > depth_outof:
						urls2.append((x, depth_outof + 1))
		else:
			for x in urls:
				if self.DEPTH >= depth and depth_outof == -1:
					urls2.append((x, -1))
				else:
					assert self.DEPTH + depth_outof + 1 == depth
					if self.DEPTH_OUTOF > depth_outof:
						urls2.append((x, depth_outof + 1))
		urls = urls2
		for url, new_depth_outof in urls:
			print 'yield...', url, depth, new_depth_outof
			req = scrapy.Request(url, meta={'depth': depth + 1, 'src_url': response.url, 'depth_outof': new_depth_outof})
			# filter!
			#if not hasattr(self, 'REQUESTS_SEEN'):
			#	self.REQUESTS_SEEN = open('requests.seen', 'rb').read()
			#	~~~
			#
			yield req
		###

if __name__ == '__main__':
	process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
	})

	process.crawl(GeneralSpider)
	process.start() # the script will block here until the crawling is finished