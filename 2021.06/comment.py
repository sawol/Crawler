try:
    from datetime import datetime, timedelta
    from bs4 import BeautifulSoup
    import re
    import json
    import requests
    from typing import List, Dict
except ModuleNotFoundError as a:
    print(a, ", please install the module!")


class Comments:
    """
    댓글 작성자 / 댓글 내용 / 댓글 작성 시간 / 좋아요 수 / 싫어요 수
    """
    article_url: str

    def __init__(self, url):
        self.article_url = url
        self.token: str = ''
        self.comment_html: str = ''
        self.comments: List[dict] = []

    def _get_html(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def create_token(self) -> None:
        soup = self._get_html(self.article_url)
        data_clint_id = soup.find('div', 'alex-action')['data-client-id']
        token_url: str = f'https://comment.daum.net/oauth/token?grant_type=alex_credentials&client_id={data_clint_id}'
        token_json = requests.get(token_url, headers={'referer': token_url}).json()
        self.token = f"bearer {token_json['access_token']}"

    def get_comments(self) -> None:
        article_num: str = self.article_url.split('/')[-1]
        comment_num: int = 0

        while True:

            comment_url: str = 'https://comment.daum.net/apis/v1/posts/@' + str(article_num) + '/comments?offset=' + str(
                comment_num) + '&limit=100&sort=RECOMMEND'
            comments = requests.get(comment_url, headers={"Authorization":self.token}).json()
            if not comments:
                break

            for comment in comments:
                comment_info = {}
                comment_info['comment user'] = self._user(comment)
                comment_info['comment date'] = self._date(comment)
                comment_info['comment content'] = self._content(comment)
                comment_info['like'] = self._like(comment)
                comment_info['unlike'] = self._unlike(comment)
                self.comments.append(comment_info)
            comment_num += 100

    def _user(self, comment) -> str:
        user = comment['user']['displayName']
        return user

    def _date(self, comment) -> str:
        date = comment['createdAt']
        return date

    def _content(self, comment) -> str:
        content = comment['content']
        content = content.replace('\n', '')
        return content

    def _like(self, comment) -> int:
        like = comment['likeCount']
        return like

    def _unlike(self, comment) -> int:
        unlike = comment['dislikeCount']
        return unlike
