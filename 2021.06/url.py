try:
    from datetime import datetime, timedelta
    from bs4 import BeautifulSoup
    import re
    import json
    import requests
    from typing import List
except ModuleNotFoundError as a:
    print(a, ", please install the module!")


class URL:

    def __init__(self, category: str, date: str):
        self.category: str = category
        self.date: str = date
        self._page_urls = []
        self. news_urls = []

    def get_news_page(self) -> None:
        """
        카테고리와 날짜 내에 모든 기사 페이지 생성하기
        ex - 1 페이지, 2 페이지
        :return: None
        """
        page_num = 1
        while True:
            page_url = f'https://news.daum.net/breakingnews/{self.category}?page={page_num}&regDate={self.date}'
            response = requests.get(page_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            page_news_board = soup.find('div', 'box_etc')
            page_not_exist = page_news_board.find('p', 'txt_none')
            if page_not_exist:
                break
            else:
                self._page_urls.append(page_url)
                page_num += 1

    def get_all_news_url(self) -> None:
        """
        get_news_url_in_page() 함수에 모든 page url를 넘김
        즉, 모든 페이지내의 기사 url를 가져옴
        :return: None
       """
        for page_url in self._page_urls:
            self.news_urls += self.get_news_url_in_page(page_url)

    def get_news_url_in_page(self, page_url) -> List[str]:
        """
        해당 페이지의 내의 모든 기사 url을 리스트로 반환
        :return: list
        """
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        page_news_board = soup.find('div', 'box_etc')
        news_url = [u['href'] for u in page_news_board.find_all('a', 'link_txt')]
        return news_url


