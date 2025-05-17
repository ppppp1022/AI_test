import sys
import json
import logging
from plyer import notification

import google.generativeai as genai

# 🔧 로그 설정
logging.basicConfig(
    filename="native_host.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def send_notification(message):
    try:
        notification.notify(title="알림", message=message, timeout=3)
        logging.info(f"Notification sent: {message}")
    except Exception as e:
        logging.error(f"Notification error: {e}")

def read_message():
    try:
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
            logging.warning("No raw length received.")
            return None
        message_length = int.from_bytes(raw_length, byteorder="little")
        message = sys.stdin.buffer.read(message_length).decode("utf-8")
        logging.info(f"Message received: {message}")
        return json.loads(message)
    except Exception as e:
        logging.error(f"Error reading message: {e}")
        return None

# 🔁 메인 루프
logging.info("Native host script started.")
logging.info(genai.__version__)

while True:
    msg = read_message()
    if msg is None:
        logging.info("No message or terminated. Exiting loop.")
        break
    url = msg.get("url", "")
    logging.info(f"URL checked: {url}")
    if "youtube.com" in url:
        send_notification("Youtube에 접속했습니다")
logging.info("Native host script exited.")
