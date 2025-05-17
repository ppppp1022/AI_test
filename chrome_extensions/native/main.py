import sys
import json
import logging
from plyer import notification

import requests
from bs4 import BeautifulSoup

import google.generativeai as genai

_available_webpage = ['www.mk.co.kr', 'www.joongang.co.kr', 'www.hani.co.kr', 'www.donga.com']

# 🔧 로그 설정
logging.basicConfig(
    filename='native_host.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def send_notification(message):
    try:
        notification.notify(title='알림', message=message, timeout=3)
        logging.info(f'Notification sent: {message}')
    except Exception as e:
        logging.error(f'Notification error: {e}')

def read_message():
    try:
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
            logging.warning('No raw length received.')
            return None
        message_length = int.from_bytes(raw_length, byteorder='little')
        message = sys.stdin.buffer.read(message_length).decode('utf-8')
        logging.info(f'Message received: {message}')
        return json.loads(message)
    except Exception as e:
        logging.error(f'Error reading message: {e}')
        return None

def send_response(data):
    response = json.dumps(data).encode('utf-8')
    sys.stdout.buffer.write(len(response).to_bytes(4, byteorder='little'))
    sys.stdout.buffer.write(response)
    sys.stdout.buffer.flush()
    logging.info(f"Sent: {data}")

def crawl_news_article(url):
    '''
    주어진 URL의 기사 본문을 크롤링하는 함수.
    매일경제, 중앙일보, 한겨레, 동아일보를 지원합니다.

    Args:
        url (str): 기사 URL

    Returns:
        str: 추출된 기사 본문 텍스트, 실패 또는 지원하지 않는 신문사일 경우 메시지 반환
    '''
    try:
        # 웹페이지 내용 가져오기
        logging.info(f'Start crawling from {url}')
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) # User-Agent 추가하여 봇 차단 방지 시도
        response.raise_for_status() # HTTP 오류 발생 시 예외 발생

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- 신문사별 본문 선택자 정의 ---
        # 제공받은 정보를 바탕으로 신문사별 본문 영역의 CSS 선택자를 정의합니다.
        article_selectors = {
            'mk.co.kr': {'selector': 'div.sec_body', 'name': '매일경제'},
            'joongang.co.kr': {'selector': 'div.article_body', 'name': '중앙일보'}, # id='article_body'도 가능하지만 class가 더 일반적
            'hani.co.kr': {'selector': 'div.article-text', 'name': '한겨레'},
            'donga.com': {'selector': 'section.news_view', 'name': '동아일보'},
            # 필요하다면 여기에 다른 신문사를 추가할 수 있습니다.
        }

        # URL을 통해 신문사 판단 및 선택자 찾기
        target_selector = None
        news_site_name = '알 수 없음'
        for site_keyword, selector_info in article_selectors.items():
            if site_keyword in url:
                target_selector = selector_info['selector']
                news_site_name = selector_info['name']
                break

        if not target_selector:
            logging.warning(f'{url} is not available url.')
            return ''

        logging.info(f'"{news_site_name}" attempt to extract article body (selector: {target_selector})')

        # 선택자로 본문 요소 찾기
        article_element = soup.select_one(target_selector)

        if article_element: 
            # 요소에서 텍스트 추출 (하위 태그의 텍스트도 포함)
            # 불필요한 요소(예: 광고, 기자 정보 끝부분 등)는 추가적인 처리가 필요할 수 있습니다.
            # 여기서는 간단히 모든 텍스트를 가져옵니다.
            article_body = article_element.get_text(separator='\n', strip=True)

            # 추출된 텍스트 정리 (예: 빈 줄 제거)
            article_body = '\n'.join([line.strip() for line in article_body.splitlines() if line.strip()])

            return article_body
        else:
            logging.warning(f'{news_site_name} - Cannot fine')
            return f'{news_site_name} - Could not find article body element. (selector: {target_selector})'

    except requests.exceptions.RequestException as e:
        logging.error(f'An error occurred while retrieving URL: {e}')
        return ''
    except Exception as e:
        logging.error(f'An error occurred while crawling: {e}')
        return ''

# 메인 루프
logging.info('Native host script started.')

while True:
    msg = read_message()
    if msg is None:
        break

    msg_type = msg.get("type")

    if msg_type == "user_input":
        prompt = msg.get("prompt", "")
        logging.info(f"User input received: {prompt}")
        send_response({"type":"chunk", "data": prompt})
        continue

    elif msg_type == "url":
        url = msg.get("url", "")
        logging.info(f"URL checked: {url}")
        splited_url = url.split('/')
        if len(splited_url) > 2 and splited_url[2] in _available_webpage:
            if splited_url[-1].isdigit():
                crawled = crawl_news_article(url)
                # with open('crawled text.txt', 'w') as f:
                    # f.write(crawled)
        continue

    else:
        logging.warning(f"Unknown message type: {msg_type}")


logging.info('Native host script exited.')
