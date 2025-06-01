import sys
import json
import logging
from plyer import notification

import requests
from bs4 import BeautifulSoup

import google.generativeai as genai
from IPython.display import Markdown
import textwrap

_available_webpage = ['www.mk.co.kr', 'www.joongang.co.kr', 'www.hani.co.kr', 'www.donga.com']
_MODEL = 'gemini-2.0-flash'

# 로그 설정
logging.basicConfig(
    filename='native_host.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def to_markdown(text):
    text = text.replace("•", "  *")
    return Markdown(textwrap.indent(text, "> ", predicate=lambda _: True))

genai.configure(api_key='AIzaSyBrHMVvqui_squRfTgU-_kF2AcoAYXlzmc')

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
bias_analyzer_model = genai.GenerativeModel(
    _MODEL,
    system_instruction = '웹 페이지를 크롤링 한 결과가 주어지면 \
        해당 크롤링 결과의 편향성 스펙트럼을 분석해서 \
        -5에 가까울 수록 극좌, 5에 가까울 수록 극우로 판단 하여 \
        JSON schema로 답할 것.:{{\
        "편향도": <-5~5 사이의 숫자>, "근거": <세 문장 이내>\
        }}',
    generation_config={"response_mime_type": "application/json"}
)
logging.info(f'Selected gemini model: {_MODEL}')
bias_analyzer = bias_analyzer_model.start_chat(history=[])
article_analyzer = genai.GenerativeModel(
    _MODEL,
    system_instruction='어떤 한 사람이 읽은 기사의 웹 크롤링 결과와\
    그 기사를 읽은 사람의 요청이 주어지면 웹 크롤링 결과를 바탕으로 요청에 답할 것.\
    이때, JSON schema로 답할 것.:{{\
    "결과": <요청에 대한 대답으로 세 문장 이내>\
    }}',
    generation_config={"response_mime_type": "application/json"}
).start_chat(history=[])

discuss_simul_model = genai.GenerativeModel(
    _MODEL,
    system_instruction='만약 한 사람이 이때까지 읽은 기사의 analysis history를 추가적인 입력으로 읽었으면, \
        해당 뉴스 기사 요약 결과의 편향성 스펙트럼을 분석해서 \
        -5에 가까울 수록 극좌, 5에 가까울 수록 극우로 판단 하여 \
        점수가 -1 미만인 A, 점수가 1 초과인 B의 토론을 시연할 것. \
        토론 주제는 한 가지로 정하여 토론할 것.\
        이때, 각 문장은 세 문장 이내로 답하며 다음의 JSON schema로 답할 것.:{{\
        "A1": <A가 첫 번째로 말할 말>, "B1": <B가 A1 다음으로 말할 말>,\
        "A2": <A가 B1 다음으로 말할 말>, "B2": <B가 A2 다음으로 말할 말>,\
        "A3": <A가 B2 다음으로 말할 말>, "B3": <B가 A3 다음으로 말할 말>\
        }} \
        만약 한 사람의 읽은 기사가 아닌 개인의 의견이 입력으로 들어왔을 경우\
        그 의견에 대해서 A의 입장과 B의 입장을 답할 것.\
        이때, 각 문장은 세 문장 이내로 답하며 다음의 JSON schema로 답할 것.:{{\
        "A1": <A가 의견에 대해 말할 말>, "B1": <B가 의견에 대해 말할 말>\
        }}',
    generation_config={"response_mime_type": "application/json"}
)
discuss_simul = discuss_simul_model.start_chat(history=[])
logging.info(f'model all loaded')

_user_bias = []
_article_history = []
_discussion = False

while True:
    try:
        msg = read_message()
        if msg is None:
            break

        msg_type = msg.get("type")

        if msg_type == "user_input":
            prompt = msg.get("prompt", "")
            logging.info(f"User input received: {prompt}")
            if _discussion:
                discuss_result = discuss_simul.send_message(prompt)
                discuss_result = json.loads(discuss_result.text)
                logging.info(discuss_result)
                send_response({"type": "chunk", "from": "인물 A", "data": discuss_result["A1"]})
                send_response({"type": "chunk", "from": "인물 B", "data": discuss_result["B1"]})
            else:
                article_result = json.loads(article_analyzer.send_message((_article_history[-1], prompt)).text)
                logging.info(article_result)
                send_response({"type": "chunk", "from": "인물 A", "data": article_result["결과"]})
            continue

        elif msg_type == "url":
            url = msg.get("url", "")
            logging.info(f"URL checked: {url}")
            splited_url = url.split('/')
            if len(splited_url) > 2 and splited_url[2] in _available_webpage:
                if splited_url[-1].isdigit():
                    crawled = crawl_news_article(url)
                    analyze_result = bias_analyzer.send_message(crawled)
                    analyze_result = json.loads(analyze_result.text)
                    _user_bias.append(analyze_result["편향도"])
                    _article_history.append(analyze_result["근거"])
                    logging.info(f'Average of user bias {sum(_user_bias) / len(_user_bias)}')
                    logging.info(f'Bias is {analyze_result["편향도"]}, reason is {analyze_result["근거"]}')
            if abs(sum(_user_bias) / len(_user_bias) ) > 3:
                send_notification("흠... 다른 성향의 기사도 찾아보는 건 어떤가요?")
            continue

        elif msg_type == "disscus":
            logging.info(f'Disscus simmulation started')
            if len(_article_history) <= 2:
                logging.info(f'Article History is too short. len={len(_article_history)}')
                send_response({"type": "chunk", "from": "AI", "data": "Too short history. Please visit more articles."})
                continue

            _discussion = True
            discuss_result = discuss_simul.send_message(_article_history)
            discuss_result = json.loads(discuss_result.text)
            logging.info(discuss_result)
            send_response({"type": "chunk", "from": "인물 A", "data": discuss_result["A1"]})
            send_response({"type": "chunk", "from": "인물 B", "data": discuss_result["B1"]})
            send_response({"type": "chunk", "from": "인물 A", "data": discuss_result["A1"]})
            send_response({"type": "chunk", "from": "인물 B", "data": discuss_result["A2"]})
            send_response({"type": "chunk", "from": "인물 A", "data": discuss_result["A3"]})
            send_response({"type": "chunk", "from": "인물 B", "data": discuss_result["B3"]})

        else:
            logging.warning(f"Unknown message type: {msg_type}")
    except Exception as e:
        logging.error(f'An error occurred: {e}')

logging.info('Native host script exited.')
