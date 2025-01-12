import json
import asyncio
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# set up
connected_clients = set()
current_dir = os.path.dirname(__file__)
config_path = os.path.join(current_dir, 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)


def process_return_msg(data = 'null', status = 'success', retcode = '', echo = ''):
    ret = {
        'status': status,
        'retcode': retcode,
        'data': json.dumps(data),
        'echo': echo
    }
    return json.dumps(ret)

async def send_group_msg(msg):
    await broadcast_message("这是一个广播消息")
    return f"发送群消息: {msg['message']}"

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
                response = actions[action](*params)
                await websocket.send(response)
            else:
                await websocket.send(f"未知动作: {action}")
    finally:
        connected_clients.remove(websocket)

async def broadcast_message(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data_action = json.loads(post_data)
        action = data_action['action']
        params = data_action.get('params', [])
        if action in actions:
            response = actions[action](*params)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("Unknown command")
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