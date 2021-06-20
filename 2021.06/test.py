from url import URL
from article import Article
from comment import Comments


def test_url_list(category: str, date: str) -> list:
    """
    해당 날짜에 모든 url을 가져오는 테스트
    category = IT: digital, 사회: society, 정치: politics, 경제: economic, 연예: entertain, 스포츠: sports
    :return:
    """
    url = URL(category, date)
    url.get_news_page()
    url.get_all_news_url()
    all_news_url = url.news_urls
    print(f'기사 url 수 : {len(all_news_url)}')
    return all_news_url

def test_article(url) -> dict:
    """
    기사 url / 기사 제목 / 입력 시간 / 기사 내용 / 를 반환하는지 체크
    :return:
    """
    art = Article(url)
    article = art.get_article()
    return article

def test_comments(url: str) -> list:
    """
    댓글 작성자 / 댓글 내용 / 댓글 작성 시간 / 좋아요 수 / 싫어요 수 를 반환하는지 체크
    :return:
    """
    comments = Comments(url)
    comments.create_token()
    comments.get_comments()
    comments = comments.comments
    return comments


if __name__ == '__main__':
    all_news_url: list = test_url_list('digital', '20210621')

    for news_url in all_news_url:
        article = test_article(news_url)
        comments = test_comments(news_url)
        if not comments:
            comments = '댓글이 없습니다.'
        print(article, comments)
