# -*- coding: utf-8 -*-
import scrapy
import json
from Project.items import ProjectItem
import base64, zlib

# url list spider
# input : urls to crawl
# output : crawled data
class SpiderSpider(scrapy.Spider):
	name = "Spider"

	def gen_queue(self):
		if self.state.get('MyQueue', None) == None:
			print 'INITEDINITEDINITEDINITEDINITEDINITEDINITEDINITEDINITEDINITEDINITEDINITEDINITEDINITEDINITEDINITED'
			self.state['MyQueue'] = []
		l = len(self.crawler.engine.slot.scheduler)
		THR = 100
		if l < THR: 
			i = 0
			while i < THR - l and len(self.state['MyQueue']) > 0:
				url, meta, callback = self.state['MyQueue'].pop(0)
				if callback == 'parse_process':
					callback = self.parse_process
				else:
					assert 0
				print(url, )
				yield scrapy.Request(url, meta=meta, callback=callback, dont_filter=True)
				i += 1

	def parse_process(self, response):
		one = {'src_url': response.meta['src_url'], 'url': response.meta['url'], 'label': response.meta['label']}
		with open('did.txt', 'a') as f:
			f.write(str(one) + '\n')
		item = ProjectItem()
		item['src_url'] = response.meta['src_url']
		item['url'] = response.meta['url']
		item['label'] = response.meta['label']
		item['body'] = base64.b64encode(zlib.compress(response.body, 9))
		item['encoding'] = response.encoding
		yield item
		for x in self.gen_queue():
			yield x

	def start_requests(self):
		print 'STARTING LOADING...........'
		jo = json.loads(open(r'D:\ctf\out.json', 'rb').read())
		self.state['MyQueue'] = []
		for x in jo:
			self.state['MyQueue'].append((x['url'], x, 'parse_process'))
		for x in self.gen_queue():
			yield x
		print 'LOADED.................'

