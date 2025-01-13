import json
import asyncio
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import time
from message_convert import message_convert
convert = message_convert()
current_dir = os.path.dirname(__file__)
config_path = os.path.join(current_dir, 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)


connected_clients = set()
def process_return_msg(data = 'null', status = 'success', retcode = '', echo = ''):
    ret = {
        'status': status,
        'retcode': retcode,
        'data': json.dumps(data),
        'echo': echo
    }
    return json.dumps(ret)

def time1():
    return int(time.time())
async def send_group_msg(msg):
    message = msg['message']
    try:
        message[0]['type']
        raw_message = convert.array2cq(message, False)
    except:
        raw_message = convert.array2cq(convert.cq2array(message, False), True)
    msg_id = 0
    print(msg, "msg")
    user_id = msg['user_id']
    print(user_id, "user_id")
    event_data = {
    "self_id": 0,
    "user_id": 0,
    "time": time1(),
    "message_id": msg_id,
    "message_seq": msg_id,
    "real_id": msg_id,
    "message_type": "group",
    "sender": {
        "user_id": user_id,
        "nickname": "Test User",
        "card": "",
        "role": "member"
    },
    "raw_message": raw_message,
    "font": 14,
    "sub_type": "normal",
    "message": convert.cq2array(raw_message, True),
    "message_format": "array",
    "post_type": "message",
    "group_id": msg['group_id'],
}
    await broadcast_message(json.dumps(event_data, ensure_ascii=False))
    return """{"message": "success"}"""

actions = {
    "send_group_msg": send_group_msg
}
async def websocket_handler(websocket, path=None):
    print("🔰 新客户已加入")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"⭐ WebSocket 收到消息: {message}")
            data_action = json.loads(message)
            action = data_action['action']
            params = data_action.get('params', [])
            if action in actions:
                response = await actions[action](params)
                await websocket.send(response)
            else:
                await websocket.send(f"未知动作: {action}")
    except websockets.exceptions.ConnectionClosed:
        print("🔴 客户端断开连接")
    finally:
        connected_clients.remove(websocket)

async def broadcast_message(message):
    if connected_clients:
        await asyncio.wait([asyncio.create_task(client.send(message)) for client in connected_clients])

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    def do_OPTIONS(self):
        self._set_headers()
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = json.loads(post_data)
        action = self.path.lstrip('/')
        if action in actions:
            response = asyncio.run(actions[action](params))
            self.send_response(200)
            self._set_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(400)
            self._set_headers()
            self.wfile.write("未知动作")
async def start_websocket_server():
    if config['ws-server']['switch']:
        print("🚀 正在启动 WebSocket 服务器")
        async with websockets.serve(websocket_handler, "localhost", config['ws-server']['port']):
            print(f"✅ WebSocket 服务器 已在 localhost:{config['ws-server']['port']} 启动")
            await asyncio.Future()  # 保持服务器运行

def start_http_server():
    if config['http-server']['switch']:
        print("🚀 正在启动 HTTP 服务器")
        httpd = HTTPServer(('localhost', config['http-server']['port']), SimpleHTTPRequestHandler)
        print(f"✅ HTTP 服务器 已在 localhost:{config['http-server']['port']} 启动")
        httpd.serve_forever()

async def main():
    print("⚙ 读取设置中...")
    try:
        await asyncio.gather(
            start_websocket_server(),
            asyncio.to_thread(start_http_server)
        )
    except OSError as e:
        print(f"⛔ 启动失败: {e}")
        print("⚠ 启动失败😡")

if __name__ == "__main__":
    asyncio.run(main())