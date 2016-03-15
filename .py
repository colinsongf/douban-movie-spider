# -*- coding: utf-8 -*-
import re
import time
from urllib import request
import pymongo


# 获取url的html内容
def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/48.'
                      '0.2564.116 Chrome/48.0.2564.116 Safari/537.36',
        'pgrade-insecure-requests': '1',
        ':host': 'www.douban.com',
        'cookie': 'bid="GhPm4Wltquk"; __utma=30149280.1923340589.1457364203.1457364203.1457444423.2; __utmz=30'
                  '149280.1457444423.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ll="108309"; dbcl2="89'
                  '718263:pliQuc4rCo4"; ct=y; ck="hPcq"; ap=1; __ads_session=TNpLaTSpsAhx3f5K/QA=; push_noty_nu'
                  'm=0; push_doumail_num=0',
        'referer': 'https://www.douban.com/tag/2014/movie'
    }
    req = request.Request(url, headers=headers)
    response = request.urlopen(req)
    html = response.read()
    return html


# 从列表页获取所有电影的url，写入urls.txt
def get_urls():
    n = 1
    pages = 34
    f = open('urls.txt', 'w+')
    for i in range(pages):
        if i == 0:
            url = 'https://www.douban.com/tag/2014/movie'
        else:
            url = 'https://www.douban.com/tag/2014/movie?start=' + str(15*i)
        html = get_html(url)
        time.sleep(2)
        pattern = re.compile('<dd>.*?<a href="(.*?)" class="title" target="_blank">', re.S)
        mains = re.findall(pattern, html)
        for main in mains:
            f.write(main + '\n')
            n += 1
    
        
# 到每个电影的主页爬取信息
def crawler():
    n = 1
    for line in open('urls.txt'):
        html = get_html(line).decode('utf-8')
        pattern = re.compile('"v:itemreviewed">(.*?)</span>.*?'
                             '"year">\((.*?)\)</span>.*?'
                             '制片国家/地区:</span> (.*?)<br/>', re.S)
        pattern_language = re.compile('语言:</span> (.*?)<br/>', re.S)
        pattern_director = re.compile('"v:directedBy">(.*?)</a>', re.S)
        pattern_average = re.compile('"v:average">(.*?)</strong>', re.S)
        pattern_votes = re.compile('"v:votes">(.*?)</span>', re.S)
        pattern_actors = re.compile('"v:starring">(.*?)</a>', re.S)
        pattern_genres = re.compile('"v:genre">(.*?)</span>', re.S)
        details = re.findall(pattern, html)
        language = re.findall(pattern_language, html)
        director = re.findall(pattern_director, html)
        average = re.findall(pattern_average, html)
        votes = re.findall(pattern_votes, html)
        actors = re.findall(pattern_actors, html)       # 有些电影没有  演员|评分|导演|评分&评价人数|语言
        genres = re.findall(pattern_genres, html)
        values = {}
        conn = pymongo.MongoClient('localhost', 27017)
        movie_db = conn.movie
        movie_info = movie_db.info
        # print(details)
        if details[0][0].find("'"):
                values['title'] = details[0][0].replace("&#39;", "'")
        else:
                values['title'] = details[0][0]
        values['year'] = details[0][1]
        values['country'] = details[0][2]
        values['genres'] = genres
        if director:
                values['director'] = director[0]
        if language:
                values['language'] = language[0]
        if average[0]:
                values['average'] = average[0]
        if votes:
                values['votes'] = votes[0]
        if actors:
                values['actors'] = actors
        movie_info.insert(values)
        print('the %dth movie written' % n)
        n += 1
        time.sleep(2)


# 库的查询
def lookup():
    connection = pymongo.MongoClient('localhost', 27017)
    db = connection.movie
    info = db.info
    for item in info.find():
        print(item['title'])
    # db.info.remove()
    # print(info.find().count())
    
# get_urls()

# start = time.time()
# crawler()
# end = time.time()
# print('time:%ds' % (end - start))

# lookup()
