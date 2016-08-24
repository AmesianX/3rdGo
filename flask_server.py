from flask import Flask, request, render_template, Markup
import process
from settings import DATA_DIR
import os

app = Flask(__name__)
#data = process.load_json(r'D:\ctf\scrapy\Project\general.jsonline')

@app.route('/')
def index():
	global data
	keywords = request.args.get('keywords', '')
	keywords = str(keywords)
	lis = Markup()
	if keywords != '':
		for x, src in process.search_preprocessed(keywords):
			tags = x['tags'] if src == None else src['tags']
			prob_name = x['prob_name'] if src == None else src['prob_name']
			lis += Markup(u'<li><a href="%s">%s</a><p>%s</p></li>') % (unicode(x['url']), unicode(prob_name), 'ccc')
	return render_template('search.html', lis = lis)

if __name__ == "__main__":
    app.run()
