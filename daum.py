#!/usr/bin/env python
# coding: utf-8

# In[1]:


try:
    import requests
    from bs4 import BeautifulSoup
    from urllib import parse
    import datetime
    import re
    import time
    import requests
    import json 
    import pandas as pd
    from urllib.parse   import quote
    import math
    import time
    from datetime import datetime, timedelta
    from selenium import webdriver

except ModuleNotFoundError as a:
    print(a , ", please install the module!")


# In[10]:


start1 = time.time()  # 시작 시간 저장

def content_info(url, keyword):
    # 게시글의 제목/ 날짜/ 게시글내용/ 댓글 등
    page_move = requests.get(url)
    page_move = BeautifulSoup(page_move.content, "html.parser")
    get_token = page_move.select('div.alex-area')[0]['data-client-id']
    get_token = 'https://comment.daum.net/oauth/token?grant_type=alex_credentials&client_id=' + get_token
    get_token = requests.get(get_token, headers = {'referer': url}).json()
    get_token = "bearer"+get_token['access_token']
    try:
        comment_result = []
        articleNum = url.split('/')[-1]
        try:
            result = requests.get(url)
        except:
            time.sleep(2)
            result = requests.get(url)
        page_move = BeautifulSoup(result.content, "html.parser")
        # 기사 제목 입력
        title = page_move.find('h3', class_='tit_view').text
        # 기사 작성시간 입력
        write_time = page_move.find('span', class_='txt_info', string = re.compile('입력 2')).text
        write_time = write_time.replace('입력 ', '')
        write_time = str(datetime.strptime(write_time, "%Y.%m.%d. %H:%M"))
        # 기사 수정시간 입력
        try:
            modify_time = page_move.find('span', class_='txt_info', string = re.compile('수정 2')).text
            modify_time = modify_time.replace('수정 ', '')
            modify_time = str(datetime.strptime(modify_time, "%Y.%m.%d. %H:%M"))
        except AttributeError:
    #             print('기사를 수정하지않아 수정시간이 존재하지 않음')
            pass
        # 기사 내용 입력
        contents = page_move.find('div', class_= 'article_view').text
        # 공감 수 입력
        like_url = 'http://like.daum.net/item/news/'+articleNum+'.json'
        get_like = requests.get(like_url).text+('}')
        json_like = json.loads(get_like[get_like.find('{'):get_like.rfind('}')])# 다음은 좋아요/싫어요는 없어서 공감을 좋아요로 하고 싫어요는 빈칸
        #댓글 얻기
        start_num = 0

        while True:
#             print(url)
            comment_url = 'https://comment.daum.net/apis/v1/posts/@'+str(articleNum)+'/comments?offset='+str(start_num)+'&limit=100&sort=RECOMMEND'          
            get_comments = requests.get(comment_url, headers={"Authorization":get_token}).json()
            start_num = start_num + 100
#             print(get_comments, '에러')
        #     comment_result = []
            if (not get_comments) or type(get_comments) == dict:
                contents_info = {}
                contents_info['title'] = title
                contents_info['content'] = contents
                contents_info['write_time'] = write_time
                try:
                    contents_info['modify_time'] = modify_time
                except UnboundLocalError:
                    contents_info['modify_time'] = ''
                contents_info['url'] = url
                contents_info['like_count'] = json_like['data']['likeCount']
                contents_info['angry_count'] = ''
                contents_info['recommend_count'] = ''
                contents_info['comment'] = ''
                contents_info['comment_writer_id'] = ''
                contents_info['comment_writer_nickname'] = ''
                contents_info['modTime'] = ''
                contents_info['sympathy'] = ''
                contents_info['antipathy'] = ''
                comment_result.append(contents_info)
                return comment_result

            for comments in get_comments:
                contents_info = {}
                contents_info['title'] = title
                contents_info['content'] = contents
                contents_info['write_time'] = write_time
                try:
                    contents_info['modify_time'] = modify_time
                except UnboundLocalError:
                    contents_info['modify_time'] = ''

                contents_info['url'] = url
                contents_info['like_count'] = json_like['data']['likeCount']
                contents_info['angry_count'] = ''
                contents_info['recommend_count'] = ''
                try:
                    contents_info['comment'] = comments['content']
                except TypeError:
                    contents_info['comment'] = ''
                    contents_info['comment_writer_id'] = ''
                    contents_info['comment_writer_nickname'] = ''
                    contents_info['modTime'] = ''
                    contents_info['sympathy'] = ''
                    contents_info['antipathy'] = ''
                    comment_result.append(contents_info)
                    return comment_result
                contents_info['comment_writer_id'] = ''
                try:
                    contents_info['comment_writer_nickname'] = comments['user']['displayName']
                    contents_info['modTime'] = comments['createdAt']
                    contents_info['sympathy'] = comments['likeCount']
                    contents_info['antipathy'] = comments['dislikeCount']
                    comment_result.append(contents_info)
                    #대댓글 들고오기
                    if comments['childCount'] > 0:
                        ch_startNum = 0
                        while True:
                            comment_children = 'https://comment.daum.net/apis/v1/comments/' + str(comments['id']) + '/children?offset=' + str(ch_startNum) + '&limit=100&sort=CHRONOLOGICAL'
                            ch_startNum = ch_startNum + 100
                            get_comment_children = requests.get(comment_children).json()
                            if not get_comment_children:
                                break
                            for comments_ch in get_comment_children:
                                contents_info = {}
                                contents_info['title'] = title
                                contents_info['content'] = contents
                                contents_info['write_time'] = write_time
                                try:
                                    contents_info['modify_time'] = modify_time
                                except UnboundLocalError:
                                    contents_info['modify_time'] = ''
                                contents_info['url'] = url
                                contents_info['like_count'] = json_like['data']['likeCount']
                                contents_info['angry_count'] = ''
                                contents_info['recommend_count'] = ''
                                contents_info['comment'] = comments_ch['content']
                                contents_info['comment_writer_id'] = ''
                                try:
                                    contents_info['comment_writer_nickname'] = comments_ch['user']['displayName']
                                except KeyError:
                                    print(comments, comment_url)
                                contents_info['modTime'] = comments_ch['createdAt']
                                contents_info['sympathy'] = comments_ch['likeCount']
                                contents_info['antipathy'] = comments_ch['dislikeCount']
                                comment_result.append(contents_info)
                except KeyError:
                    pass
        if title.find(keyword) >= 0 or contents.find(keyword) >= 0: #게시글, 제목에 키워드가 존재할 경우
            return len(comment_result) #모든 댓글 출력
        elif title.find(keyword) < 0 and contents.find(keyword) < 0: #게시글, 제목에 키워드가 존재하지 않을 경우
            comment_key = []
            for findkey in comment_result:
                if findkey['comment'].find(keyword) >= 0: #댓글에는 키워드가 존재할 경우 키워드 존재하는 댓글만 출력
                    comment_key.append(findkey)
            return comment_key, "댓글에 키워드존재"
    except:
        print(url)
    return comment_result
#     except Exception as e:
#         print(url, e,'에러남')
#         print('#################################')

"""
페이지별 모든 기사 url

"""
def get_page_url(date_list,keyword):
    result1 = []
    for url in date_list:
        result = requests.get(url)
        page_move = BeautifulSoup(result.content, "html.parser")
        page_select = page_move.select('em.num_page')
        pageNum = 1
        page_list = []
        # 마지막 페이지까지 기사 url 들고오기
        while page_select:
            url_pagechange = url.split('=1')
            url_pagechange = url_pagechange[0] + '=' + str(pageNum) + url_pagechange[1]
            result = requests.get(url_pagechange)
            page_move = BeautifulSoup(result.content, "html.parser")
            page_select = page_move.select('em.num_page')
            if not page_select: # 마지막 페이지가 지나면 멈추기
                break
            board_url = page_move.find('ul', class_ = "list_news2 list_allnews")
            board_url = board_url.find_all('a', class_ = "link_txt")
            for b in board_url:
                page_list = b.get('href')
                contents = content_info(page_list,keyword)
                if contents:
                    result1.append(contents)
        #     print(url, page_select)
            pageNum = pageNum +1
    return result

"""
날짜별 기사 첫 페이지 url

"""
def get_date_url(start, end, keyword):
    days_range = []
    # 날짜와 시간으로 나누기
    start = start.split(' ')
    end = end.split(' ')
    # 날짜와 시간을 datetime 형식으로 변환
    start_day = datetime.strptime(start[0], "%Y-%m-%d")
    end_day = datetime.strptime(end[0], "%Y-%m-%d")
    date_generated = [start_day + timedelta(days=x) for x in range(0, (end_day-start_day).days+1)]
    for date in date_generated:
        days_range.append(date.strftime("%Y%m%d"))
    url = []
    for i in days_range:
        url1 = 'https://news.daum.net/breakingnews/society?page=1&regDate=' + str(i)
        url.append(url1)
    return url

"""
키워드 & 날짜 검색  %20%7C%20

"""
def main():
    start = '2020-03-02 09:00:00'
    end = '2020-03-02 09:10:00'
    keyword = ' 참치뱃살맛있어'
    date_list = get_date_url(start, end, keyword)
    result = get_page_url(date_list,keyword)
#     result = content_info(page_list)
    return result
main()
print("time :", time.time() - start1)  # 현재시각 - 시작시간 = 실행 시간


# In[ ]:




