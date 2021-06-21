try:
    from datetime import datetime, timedelta
    from bs4 import BeautifulSoup
    import re
    import json
    import requests
    from typing import List, Dict
except ModuleNotFoundError as a:
    print(a, ", please install the module!")


class Article:
    """
    기사 url / 기사 제목 / 입력 시간 / 기사 내용 /
    """

    def __init__(self, url: str):
        self.url: str = url
        self.article: Dict[str,str] = {'url': self.url, 'title': None, 'create date': None, 'content': None}
        self.soup: str = ''

    def _get_html(self):
        response = requests.get(self.url)
        self.soup = BeautifulSoup(response.content, 'html.parser')

    def _get_title(self):
        self.article['title'] = self.soup.title.text

    def _get_date(self):
        self.article['create_date'] = self.soup.find('span', 'num_date').text

    def _get_context(self):
        content = self.soup.find('div', 'article_view').text
        content = content.replace('\n', '')
        self.article['content'] = content


    def get_article(self) -> dict:
        self._get_html()
        self._get_title()
        self._get_date()
        self._get_context()
        return self.article
