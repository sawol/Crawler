from datetime import datetime, timedelta
import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import json 

class news():                       # 뉴스를 가져오는 Class
    
    def __init__ (self):
        self.days_range = []
        self.news_section = {'사회':'society', '정치':'politics', 
                                '경제':'economic', '연예':'entertain', 'IT':'digital', '전체':'all'}
        self.data = {}
        self.title = []
        self.write_time = []
        self.modify_time = []
        self.contents = []
        self.like = []
        self.url = []


    def make_date(self, start: str, end: str) -> list:          # 가져 올 뉴스의 날짜를 생성
        # 날짜와 시간 분리 및 datetime 형식으로 변환
        start_day = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S").date()
        end_day = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S").date()
        start_time = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S").time()
        end_time = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S").time()

        # start_day ~ end_day 까지 리스트
        date_generated = [start_day + timedelta(days=x) for x in range(0, (end_day-start_day).days+1)]  # [datetime.date(2020, 3, 2), datetime.date(2020, 3, 3)]
        for date in date_generated:
            self.days_range.append(date.strftime("%Y%m%d")) # ['20200302', '20200303', '20200304']
        return self.days_range
    
    def get_bs(self, url: str) -> str:      # url 주소로부터 html content parser
        result = requests.get(url)
        page_content = BeautifulSoup(result.content, "html.parser")
        return page_content

    def article(self, article_url:str):      # 기사 본문에 들어가서 제목, 내용, 날짜
        articleNum = article_url.split('/')[-1]     # 기사 번호(좋아요 수, 댓글 가져올때 사용됨)
        article_html = self.get_bs(article_url)
        title = article_html.find('h3', class_='tit_view').text    # 기사 제목
        print(article_url)
        write_time = article_html.find('span', class_='num_date').text
        print(write_time)
        # write_time = write_time.replace('입력 ', '')
        write_time = str(datetime.datetime.strptime(write_time, "%Y.%m.%d. %H:%M"))      # 기사 작성시간
        try:
            modify_time = article_html.find('span', class_='txt_info', string = re.compile('수정 2')).text
            modify_time = modify_time.replace('수정 ', '')
            modify_time = str(datetime.strptime(modify_time, "%Y.%m.%d. %H:%M"))        # 기사 수정시간
        except AttributeError:
            modify_time = 0     # 수정시간 존재하지 않음
    #             print('기사를 수정하지않아 수정시간이 존재하지 않음')
            pass    
        contents = article_html.find('div', class_= 'article_view').text       # 기사 내용
        like_url = 'http://like.daum.net/item/news/'+articleNum+'.json'
        get_like = requests.get(like_url).text+('}')
        json_like = json.loads(get_like[get_like.find('{'):get_like.rfind('}')])# 다음은 좋아요/싫어요는 없어서 공감을 좋아요로 하고 싫어요는 빈칸    
        like = json_like['data']['likeCount']
        self.title.append(title)
        self.write_time.append(write_time)
        self.modify_time.append(modify_time)
        self.contents.append(contents)
        self.like.append(like)
        self.url.append(article_url)

    def get_page_url(self, section) -> list:         # 원하는 섹션의 지정 날짜 페이지 및 기사 url 들고오기
        """
        다음 기사 페이지 형식
        https://news.daum.net/breakingnews/{section}?page={page_num}&regDate={date}
        """
        section = self.news_section[section]
        for date in self.days_range:        # 지정한 날짜 루프
            page_check = 'page_check'
            page_num = 0
            while 1:              # page_num을 증가시키다가 오류가 발생할때까지 루프
                page_num += 1
                self.url = f'https://news.daum.net/breakingnews/{section}?page={page_num}&regDate={date}'
                page_content = self.get_bs(self.url)
                page_check = page_content.select('em.num_page')     # 마지막 페이지 다음 페이지에는 페이지 선택하는 기능이 없으므로 오류 발생
                if page_check == []:
                    break
                board_urls = page_content.find('ul', class_ = "list_news2 list_allnews")     # 페이지별 기사 url
                board_urls = board_urls.find_all('a', class_ = "link_txt")
                for board_url in board_urls:
                    article_url = board_url.get('href')
                    self.article(article_url)

    def make_csv(self):     # csv로 저장
        self.data['title'] = self.title
        self.data['write_time'] = self.write_time
        self.data['modify_time'] = self.modify_time
        self.data['contents'] = self.contents
        self.data['like'] = self.like
        self.data['url'] = self.url
        data = pd.DataFrame(self.data)
        print('csv 제작중...')
        data.to_csv("daum_crawler.csv", mode='w', encoding='utf-8-sig')
        print('csv 제작완료!')

    def run(self, start, end, section):      # main 함수 기능
        self.make_date(start, end)
        self.get_page_url(section)
        self.make_csv()



class comment():                    # 댓글을 가져오는 Class

    def __init__ (self):
        pass




if __name__ == "__main__":              #직접 실행할 경우에만 if문 발동! 해당 코드를 모듈로 사용했을때와 구분짓기 위해 사용
    print('다음 뉴스 크롤러입니다.')
    start = '2020-09-06 09:00:00'
    end = '2020-09-06 08:10:00'
    section = 'IT'                      # 기사의 섹션으로는 IT, 정치, 사회, 경제 등. 전체를 수집할 수도 있음
    daum = news()
    daum.run(start, end, section)
    value = input('기사의 댓글도 수집할까요? (네/아니오')
    print('댓글 수집중' if value == '네' else '크롤링을 종료합니다')