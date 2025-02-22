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
group_path = os.path.join(current_dir, 'group.json')
user_path = os.path.join(current_dir, 'user.json')
msg_data = [] # ! 用于存储消息
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
with open(group_path, 'r', encoding='utf-8') as f:
    group = json.load(f)
with open(user_path, 'r', encoding='utf-8') as f:
    user = json.load(f)
    
connected_clients = set()
def process_return_msg(data = 'null', status = 'success', retcode = '', echo = ''):
    ret = {
        'status': status,
        'retcode': retcode,
        'data': data,
        'echo': echo
    }
    return json.dumps(ret)

def time1():
    return int(time.time())
async def get_stranger_info(info, echo=""):
    if "user_id" not in info:
        return process_return_msg("null", "failed")
    user_id = info['user_id']
    event_data = {
        "user_id": 0,
        "nickname": user[str(user_id)],
        "sex": "unknown",
        "age": 0,
    }
    return process_return_msg(event_data, "ok", echo=echo)
async def get_group_list(info="", echo=""):
    ret = []
    for group_id, group_info in group.items():
        ret.append({
            "group_id": group_id,
            "group_name": group_info['name'],
            "member_count": len(group_info['members']),
            "max_member_count": 5000,
        })
    event_data = ret
    return process_return_msg(event_data, "ok", echo=echo)
async def get_group_info(info, echo=""):
    if "group_id" not in info:
        return process_return_msg("null", "failed")
    event_data = {
        "group_id": info['group_id'],
        "group_name": group[info['group_id']]['name'],
        "member_count": len(group[info['group_id']]['members']),
        "max_member_count": 5000,
    }
    return process_return_msg(event_data, "ok", echo=echo)
async def get_group_member_list(info, echo=""):
    if "group_id" not in info:
        return process_return_msg("null", "failed")
    ret = []
    for i in group[info['group_id']]['members'].items():
        ret.append({
            "group_id": info['group_id'],
            "user_id": i,
            "nickname": user[str(i)],
            "card": "",
            "sex": "unknown",
            "age": 0,
            "area": "unknown",
            "join_time": 0,
            "last_sent_time": 0,
            "level": "0",
            "role": "member",
            "unfriendly": "false",
            "title_expire_time": 0,
            "card_changable": "false"
        })
    event_data = ret
    return process_return_msg(event_data, "ok", echo=echo)
async def delete_msg(msg, echo=""):
    if "message_id" not in msg:
        return process_return_msg("failed: message param not found", "failed")
    for i in msg_data:
        if i['message_id'] == msg['message_id']:
            msg_data.remove(i)
            event_data = {
                "time": time1(),
                "self_id": 0,
                "post_type": "notice",
                "notice_type": "group_recall",
                "group_id": i['group_id'],
                "user_id": i['sender']['user_id'],
                "nick": user[str(i['sender']['user_id'])],
                "operator_id": 0,
                "message_id": msg['message_id'],
            }
            await broadcast_message(json.dumps(event_data, ensure_ascii=False))
            return process_return_msg(None, "ok", echo=echo)
    return process_return_msg("failed: message not found", "failed")

async def set_group_ban(msg, echo=""):
    if "group_id" not in msg or "user_id" not in msg or "duration" not in msg:
        return process_return_msg("failed: missing params", "failed")
    event_data = {
        "time": time1(),
        "self_id": 0,
        "post_type": "notice",
        "notice_type": "group_ban",
        "sub_type": "ban",
        "group_id": msg['group_id'],
        "user_id": msg['user_id'],
        "duration": msg['duration'],
    }
    await broadcast_message(json.dumps(event_data, ensure_ascii=False))
    return process_return_msg(None, "ok", echo=echo)

async def send_group_msg(msg, echo=""):
    if "message" not in msg:
        return process_return_msg("failed: message not found", "failed")
    
    message = msg['message']
    if message == "":
        return process_return_msg("failed: message not found", "failed")
    
    if "group_id" not in msg:
        return process_return_msg("failed: group_id not found", "failed")
    if "user_id" not in msg:
        return process_return_msg("failed: user_id not found", "failed")
    if str(msg["user_id"]) not in user:
        return process_return_msg("failed: user_id not found", "failed")
    if msg['group_id'] not in group:
        return process_return_msg("failed: group_id not found", "failed")
    try:
        message[0]['type']
        raw_message = convert.array2cq(message, False)
    except:
        raw_message = convert.array2cq(convert.cq2array(message, False), True)
    msg_id = str(time1()) + str(msg['user_id']) + str(msg['group_id'])
    user_id = msg['user_id']
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
        "nickname": user[str(user_id)],
        "card": "",
        "role": "member"
    },
    "raw_message": raw_message,
    "font": 12,
    "sub_type": "normal",
    "message": convert.cq2array(raw_message, True),
    "message_format": "array",
    "post_type": "message",
    "group_id": msg['group_id'],
}
    msg_data.append(event_data)
    await broadcast_message(json.dumps(event_data, ensure_ascii=False))
    return process_return_msg({"message_id": msg_id}, "ok", echo=echo)

actions = {
    "send_group_msg": send_group_msg,
    "get_stranger_info": get_stranger_info,
    "get_group_list": get_group_list,
    "get_group_member_list": get_group_member_list,
    "get_group_info": get_group_info,
    "delete_msg": delete_msg,
    "set_group_ban": set_group_ban,
}
async def websocket_handler(websocket, path=None):
    print("🔰 新客户已加入")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"⭐ WebSocket 收到消息: {message}")
            have_data = True
            try:
                data_action = json.loads(message)
            except:
                have_data = False
            action = data_action['action']
            params = data_action.get('params', [])
            if action in actions:
                if have_data:
                    response = await actions[action](params, echo=data_action.get('echo', ''))
                else:
                    response = await actions[action]()
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
        have_data = True
        try:
            params = json.loads(post_data)
        except:
            have_data = False
        action = self.path.lstrip('/')
        if action in actions:
            if have_data:
                response = asyncio.run(actions[action](params, echo=params.get('echo', '')))
            else:
                response = asyncio.run(actions[action]())
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
    print("⚙ 以读取设置")
    print(group, user, group['114514'], user['0'])
    print(f"🌽 共加载了 { len(group) } 个群...")
    print(f"👥 共加载了 { len(user) } 个用户...")
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