import json
import asyncio
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

current_dir = os.path.dirname(__file__)
config_path = os.path.join(current_dir, 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

async def websocket_handler(websocket, path):
    print("🔰 新客户已加入")
    async for message in websocket:
        print(f"收到消息: {message}")
        await websocket.send(f"服务器收到: {message}")
        
# HTTP SERVER
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, HTTP!')

# WS SERVER
async def start_websocket_server():
    if config['ws-server']['switch']:
        print("🚀 正在启动 WebSocket 服务器")
        async with websockets.serve(websocket_handler, "localhost", config['ws-server']['port']):
            print(f"✅ WebSocket 服务器 已在 localhost:{config['ws-server']['port']} 启动")
            await asyncio.Future()  # 保持服务器运行

# START HTTP SERVER
def start_http_server():
    if config['http-server']['switch']:
        print("🚀 正在启动 HTTP 服务器")
        httpd = HTTPServer(('localhost', config['http-server']['port']), SimpleHTTPRequestHandler)
        print(f"✅ HTTP 服务器 已在 localhost:{config['http-server']['port']} 启动")
        httpd.serve_forever()

# 主函数
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