import sys
import json
from plyer import notification

def send_notification(message):
    notification.notify(title="알림", message=message, timeout=3)

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return None
    message_length = int.from_bytes(raw_length, byteorder="little")
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)

while True:
    msg = read_message()
    if msg is None:
        break
    url = msg.get("url", "")
    if "youtube.com" in url:
        send_notification("Youtube에 접속했습니다")