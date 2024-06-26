from PyQt6 import QtWidgets
import platform
import json
import websocket
import requests


class MLineEdit(QtWidgets.QLineEdit):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        filepathlist = e.mimeData().text()
        filepath = filepathlist.split('\n')[0]  # 拖拽多文件只取第一个地址
        if platform.system() == "Windows":
            filepath = filepath.replace('file:///', '')
        filepath = filepath.replace('file://', '', 1)  # 去除文件地址前缀的特定字符
        self.setText(filepath)


def readfile_scan(name):
    try:
        from pathlib import Path
        wordlist = set(Path(name).read_text().splitlines())
        htmls = [
            url.strip() if url.strip().startswith(('http://', 'https://')) else ''.join(('http://', url.strip()))
            for
            url in wordlist if len(url) > 1]
        return htmls
    except Exception as e:
        print(e)


def websocket_conn():
    # websocket_conn 连接
    try:
        resp = requests.get('http://127.0.0.1:9222/json')
        assert resp.status_code == 200
        ws_url = resp.json()[0].get('webSocketDebuggerUrl')
        return websocket.create_connection(ws_url)
    except Exception as e:
        print(f"链接cdp端口失败，请查看是否开启了调试模式 {e}")
        return e


def execute_cdp(conn: websocket, command: dict):
    # 执行  dp
    conn.send(json.dumps(command))
    # 接受websocket的响应，并将字符串转换为 dict()
    return json.loads(conn.recv())


def cdpencode(call, express):
    try:
        conn = websocket_conn()
        # js = "console.log('hello world')" # 控制台打印 hello world
        command = {
            'method': 'Debugger.evaluateOnCallFrame',  # 处理 传进去的 expression
            'id': int(),  # id需要传一个整型，否则会报错
            'params': {
                'callFrameId': call,
                'expression': express,
                'objectGroup': 'console',
                'includeCommandLineAPI': True,
            }
        }
        resp = execute_cdp(conn, command)
        print(resp)
        return resp["result"]["result"]['value']
    except Exception as e:
        return e


if __name__ == '__main__':
    callFrameId = "2900017506043058386.3.0"
    expression = 'rsa.encrypt("admin")'
