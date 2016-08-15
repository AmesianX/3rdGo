data/ : github clone한 내용들 저장.
deps/ : 먼저 설치해야 하는 것들.
scrapy/ : scrapy 크롤링 관련 소스/데이터
	Project/
		scrapy.cfg : scrapy 설정 파일
		Project/
			items.py : scrapy item 항목 파일
			settings.py : 설정 파일
			spiders/
				General.py : 특정 url부터 시작해서, 각 페이지에서 링크 추출하는식으로 계속 크롤링해주는 spider. depth/filter/depth_outof(기본 depth/filter 밖으로 크롤링하는 단계) 지정 가능함. 
				Spider.py : out.json 읽어서 그 url들을 크롤링해주는 scrapy spider.
		jobdir/ : 크롤링 할때, Ctrl + C 키로 중지 했다가 재시작할 수 있는데, 그 상태 파일이 저장되는 곳. 
		log.txt : scrapy 로그 파일. 
templates/ : flask 웹서버 html 템플릿
clone.py : init_list.txt 파일을 읽어서 해당 git url 들을 clone 하거나 checkout 해줌. 
flask_server.py : 웹 인터페이스 웹서버. 
init_list.txt : clone.py에서 초기화할 git url 목록. 
md_data : 
out.json : 
process.py : 여러가지 처리하는 파일. preprocess, search 등등. 
test.txt : 
url_parse : clone한 git 저장소에서 url 파싱. 
