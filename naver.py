#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import datetime
import re
from naver_comment import util


class naver_comment:
    def __init__(self):
        self.total = []

    def crawlingComment(self, url, keywordlist, userlist):
        contents_list = []
        username_list = []
        moditime_list = []
        sympathy_list = []
        antipathy_list = []

        oid = url.split("oid=")[1].split("&")[0]
        aid = url.split("aid=")[1]
        page = 1

        while True:

            comment_url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + oid + "%2C" + aid + "&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + str(
                page) + "&refresh=false&sort=FAVORITE"

            # ******************
            # Comment Parsing
            # ******************
            # 속도 느린 문제점 발생. 같은 작업을 6번 반복 >> 개선 필요

            comm_cont = util.getcontents(comment_url)
            total_comm = str(comm_cont).split('comment":')[1].split(",")[0]
            content = re.findall('"contents":"(.*?)","userIdNo"', str(comm_cont))
            userName = re.findall('"userName":"([^\:]*)","userProfileImage"', str(comm_cont))
            modTime = re.findall('"modTime":"([^\*]*)","modTimeGmt"', str(comm_cont))
            sympathy = re.findall('"sympathyCount":(\d{1,6}),"antipathyCount"', str(comm_cont))
            antipathy = re.findall('"antipathyCount":(\d{1,6}),"userBlind"', str(comm_cont))
            if len(content) == 0:
                return False
            # ******************
            # Append data
            # ******************

            for i, (cmt, nick) in enumerate(zip(content, userName)):
                tmp = []
                for key in keywordlist:
                    if key in cmt:
                        tmp.append((util.clear_headline(cmt), userName[i], modTime[i], sympathy[i], antipathy[i]))
                for user in userlist:
                    if user in nick:
                        tmp.append((util.clear_headline(cmt), userName[i], modTime[i], sympathy[i], antipathy[i]))

                tmp = list(set(tmp))
                for i in tmp:
                    contents_list.append(i[0])
                    username_list.append(i[1])
                    moditime_list.append(i[2])
                    sympathy_list.append(i[3])
                    antipathy_list.append(i[4])

            contents_list = self.flatten(contents_list)
            username_list = self.flatten(username_list)
            moditime_list = self.flatten(moditime_list)
            sympathy_list = self.flatten(sympathy_list)
            antipathy_list = self.flatten(antipathy_list)

            # ******************
            # Append data
            # ******************
            if int(total_comm) <= ((page) * 20):
                break
            else:
                page += 1

        # 모든 리스트를 하나로 함치는 함수를 만들어야 함.
        if [contents_list, username_list, moditime_list, sympathy_list, antipathy_list] == [[], [], [], [], []]:
            return False

        return [contents_list, username_list, moditime_list, self.strtoint(sympathy_list), self.strtoint(antipathy_list)]

    def listVerify(self, comment_list):
        for listnum in comment_list:
            for len in range(len(comment_list) - 1):
                if (len(listnum) != len(comment_list[len + 1])):
                    print('error')
                    return False
            break
        return True

    def flatten(self, l):
        flatList = []
        for elem in l:
            if type(elem) == list:
                for e in elem:
                    flatList.append(e.replace('T', ' ').replace('+0900', ''))
            else:
                flatList.append(elem.replace('T', ' ').replace('+0900', ''))

        return flatList

    def strtoint(self, strlist):
        intlist = []
        for i in strlist:
            intlist.append(int(i))
        return intlist


class naver_news:

    def __init__(self):
        self.days_range = []
        self.total_data = []
        self.result = []
        self.comment = naver_comment()
        self.comment_column_headers = ['comment', 'userName', 'modTime', 'sympathyCount', 'antipathyCount', 'url']
        self.comment_crawldata = pd.DataFrame(columns=self.comment_column_headers)

    def makedate(self, start_time, end_time):
        start = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").date()
        end = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").date()  # 범위 + 1
        date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days + 1)]
        for date in date_generated:
            self.days_range.append(date.strftime("%Y%m%d"))
        return self.days_range

    def getmessmedia(self, contents):
        media = contents.find('ul', {'class':'massmedia'})
        return media.find('a', {'class':'visit on nclicks(cnt_press)'}).text

    def get_aid_range(self, news_url):
        try:
            new_content = util.getcontents(news_url)
            max_page_content = new_content.find('ul', {'class': 'type06_headline'})
            max_article_urls = max_page_content.findAll('dt', {'class': False})
            maxaid = max_article_urls[0].find('a')['href'].split('aid=')[1]
            media = self.getmessmedia(new_content)

            min_page_content = util.getcontents(news_url + "&page=" + str(10000))
            if min_page_content.find('dt', {'class': False}):
                min_article_urls = min_page_content.findAll('dt', {'class': False})

            else:
                last = min_page_content.find('div', {'class': 'paging'})
                max_page = last.find('strong').text
                for page in range(int(max_page), 0, -1):
                    min_article = util.getcontents(news_url + "&page=" + str(page))
                    if min_article.find('dt', {'class': False}):
                        min_article_urls = min_article.findAll('dt', {'class': False})
                        minaid = min_article_urls[-1].find('a')['href'].split('aid=')[1]
                        break
            return [int(minaid), int(maxaid)]

        except Exception as e:
            print(e)

    def get_press_list(self, news_url, page_url):
        # 언론사 주소 형태 /main/list.nhn?mode=LPOD&mid=sec&oid=001 이때 oid만 바뀜.
        urllist = []
        exclude_press = ['신화사 연합뉴스', 'AP연합뉴스', 'EPA연합뉴스']
        content = util.getcontents(page_url)
        tag = content.find_all('ul', {'class': 'group_list'})
        for press_url in tag:
            for url in press_url.find_all('a'):
                if url.text == '연합뉴스':
                    # 연합뉴스 oid, 링크가 속보로 되어 있음 그래서 별도로 추가해줌.
                    urllist.append('001')
                elif url.text not in exclude_press:
                    urllist.append((news_url + url['href']).split('oid=')[1])
        return urllist

    def get_article_title(self, document_content):
        # Get Article title
        try:
            tag_headline = document_content.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
            text_headline = ''
            text_headline = text_headline + util.clear_headline(str(tag_headline[0].find_all(text=True)))
            if not text_headline:
                pass
            return text_headline
        except IndexError:
            # 스포츠 기사일 경우 소스 형태가 달라 파싱하지 못함. 따로 처리할 순 있는데, 스포츠 기사는 필요 없다 판단하여 리턴 함.
            # 이후 기사 내용 등에서는 따로 에러처리 안함.
            return

    def get_article_comment(self, url, keywordlist, userlist):
        # Get comment count
        total = self.comment.crawlingComment(url, keywordlist, userlist)
        return total

    def strtoint_reaction(self, count):
        if count == '':
            return 0
        return int(count)

    def makedata(self, title, content, writer, write_time, reaction, url, comment):

        ['potal', 'write_time', 'modify_time', 'title', 'content', 'url', 'like_count', 'angry_count',
         'recommend_count', 'comment']
        contents_info = {
            'potal': 'naver',
            'title': title,
            'content': content,
            'writer': writer,
            'write_time': write_time['news_writedate'],
            'modify_time': write_time['news_modifydate'],
            'url': url,
            'like_count': self.strtoint_reaction(reaction['like_count']),
            'angry_count': self.strtoint_reaction(reaction['angry_count']),
            'recommend_count': self.strtoint_reaction(reaction['recommend_count']),
            'comment': comment
        }
        return contents_info

    def run(self, start_time, end_time, keyword, userlist):
        page_url = 'https://news.naver.com/main/officeList.nhn'
        news_url = 'https://news.naver.com'
        press_url = '/main/list.nhn?mode=LPOD&mid=sec&oid='
        article = '/main/read.nhn?mode=LPOD&mid=sec&oid='
        press_oid_list = self.get_press_list(news_url, page_url)
        datelist = self.makedate(start_time, end_time)

        for oid in press_oid_list:
            for date in datelist:
                newsdate = news_url + press_url + oid + '&date=' + date
                aid_range = self.get_aid_range(newsdate)
                writer = aid_range[2]
                print('{}: {} 개 기사 탐색'.format(writer, aid_range[1] - aid_range[0]))
                try:
                    for aid in range(aid_range[0], aid_range[1] + 1):
                        aritcle_url = news_url + article + oid + '&aid=' + str(aid).zfill(10)
                        comment = self.get_article_comment(aritcle_url, keyword, userlist)
                        if comment is False: continue
                        # document_content = util.getcontents(aritcle_url)
                        # title = self.get_article_title(document_content)
                        # document_content = ''
                        # if title is None: title = ''
                        urllist, titlelist, writerlist = [], [], []
                        for i in range(len(comment[0])): urllist.append(aritcle_url); #titlelist.append(title); writerlist.append(writer)
                        # comment.append(titlelist)
                        # comment.append(writerlist)
                        comment.append(urllist)
                        potal = []
                        for i in range(len(comment[0])): potal.append('naver')
                        comment_dataframe = pd.DataFrame(
                            {"potal": potal,
                             "comment": comment[0],
                             "userName": comment[1],
                             "modTime": comment[2],
                             "sympathyCount": comment[3],
                             "antipathyCount": comment[4],
                             # "title": comment[5],
                             # "writer": comment[6],
                             "url": comment[5]},
                            columns=['potal', 'comment', 'userName', 'modTime', 'sympathyCount', 'antipathyCount', 'url'])
                        self.comment_crawldata = self.comment_crawldata.append(comment_dataframe)

                except IndexError:
                    pass

        return self.comment_crawldata

if __name__ == '__main__':
    naver = naver_news()
    data = naver.run('2020-03-26 13:00:00', '2020-03-26 14:30:00', [], ['ging'])
    #comment_crawldata = data.applymap(lambda x: x.replace('\xa0','').replace('\xa9',''))
    data.to_csv('.\\result.csv', encoding='utf-8-sig')