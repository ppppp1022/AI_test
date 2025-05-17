from flask import Flask, jsonify
import threading
import os

app = Flask(__name__)

# 상태를 기본적으로 False로 설정
extension_state = False

@app.route("/toggle", methods=["POST"])
def toggle():
    global extension_state
    extension_state = not extension_state
    return jsonify({"state": extension_state})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"isOn": extension_state})

@app.route("/start", methods=["POST"])
def start():
    global extension_state
    if not extension_state:
        extension_state = True
    return jsonify({"status": "server started"})

def run_server():
    app.run(host='0.0.0.0', port=5000, threaded=True)

# 서버를 별도의 쓰레드에서 실행
if __name__ == "__main__":
    # 이미 실행 중이라면 시작하지 않도록 방지
    if os.environ.get('FLASK_RUNNING'):
        print("Flask 서버는 이미 실행 중입니다.")
    else:
        os.environ['FLASK_RUNNING'] = 'true'
        threading.Thread(target=run_server).start()

    # 메인 프로그램 종료를 막기 위해 계속 실행
    while True:
        pass
