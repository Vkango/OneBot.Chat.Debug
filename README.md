# OneBot.Chat.Debug
用于支持OneBot11协议的机器人进行消息收发测试

# 功能支持

## Server

- [x] WebSocket 服务器
- [x] HTTP POST 服务器

## API

- [x] 发送群聊消息
- [ ] 私聊消息
- [ ] 获取自身信息

## 消息内容支持

- [x] 文本
- [x] 图片
- [ ] 回复
- [ ] 转发
- [ ] JSON卡片

## Client

- [x] WebSocket 自动重连
- [x] HTTP POST API
- [x] 消息展示

# 快速开始

## LiveServer/FiveServer 的配置

在vscode settings.json中设置排除项，例如：

``````json
{
    "fiveServer.ignore": [
        "/client/images/",
        "**/client/images/**",
        "**/images/**",
        "/server/",
        "**/server/**"
    ]
}
``````

## 端口配置

服务器开放在localhost

端口可在config.json内修改

``````json
{
    "ws-server": {
        "switch" : true,
        "port": 8080
    },
    "http-server": {
        "switch" : true,
        "port": 8081
    },
    "console": {
        "printAllmessages" : true
    }
}
``````

在 `app.js` 中，您需要修改以下内容

```javascript
const ws_uri = 'ws://127.0.0.1:8080'; // 修改为目标端口
const http_url = 'http://127.0.0.1:8081' // 修改为目标端口
```

以及Bot的WS，HTTP端口配置

## 头像预处理

client - images - avatars 中，请预留 0.jpg， 1.jpg

其中，0.jpg是机器人头像，1.jpg是您的头像

## Bot的配置

由于没有登录功能，无法对来源用户进行区分

在发送群消息中，您需要指明user_id = 0

以便区分来源。

例如：

```python
def SendGroupMsg(self, groupid, msg):
    """ 发送群消息 """
    data1 = {"group_id": groupid, "message": msg, "user_id": 0}
    return self.Api_SendReq("send_group_msg", data1)
```

## 注意

`/client/images` 文件夹中的内容不会自动清理。

# 引用

背景纹理图片来自：[Transparent Textures](https://www.transparenttextures.com/)

图标素材来自NTQQ9

based on NeoChat
