// 管理消息收发
import { WSMessage } from './ws.js';
import * as Helper from './helper.js';
import { API } from './api.js';
const message_list = {}; // 用于保存消息的对象，以群号区分
const ws_uri = 'ws://127.0.0.1:8080'; // 修改为目标端口
const http_url = 'http://127.0.0.1:8081' // 修改为目标端口
let websocket = new WSMessage(ws_uri, ProcessNewMessage)
let Api = new API(http_url, websocket);
let currentGroupId = 0;
let self_id = 1; // bot id = 0
document.getElementsByClassName('status-bar-item')[0].innerHTML = 'WebSocket: ' + ws_uri + '<br>' + 'HTTP: ' + http_url;

function ProcessNewMessage(event) {
    ////////////////////////////////////////////////////////////
    // 更新对话列表
    const message = JSON.parse(event.data);
    displayMessage({
        text: message.message,
        avatar: './images/avatars/' + message.sender.user_id + '.jpg',
        user_id: message.sender.user_id,
        id: message.real_id,
    });
};
async function sendMessage() {
    const messageInput = document.getElementById('message');
    const message = messageInput.value.trim();
    if (message) {
        try {
            await Api.SendGroupMessageHTTP(currentGroupId, message);
            messageInput.value = '';
        }
        catch (error) {
            console.error('消息发送失败：', error);
        };

    }
}

function displayMessage(message) {
    const messagesContainer = document.getElementsByClassName('messages')[0];
    if (messagesContainer) {
        const isScrolledToBottom = messagesContainer.scrollHeight - messagesContainer.clientHeight <= messagesContainer.scrollTop + 1;
        let message_html = ""
        for (let i = 0; i < message.text.length; i++) {

            if (message.text[i].type == "text") {
                let text = message.text[i].data.text;
                text = text.replace(/&/g, "&amp;")
                           .replace(/\[/g, "&#91;")
                           .replace(/\]/g, "&#93;")
                           .replace(/\n/g, "<br>");
                message_html += text;
            }


            else if (message.text[i].type == "image") {
                message_html += `<img id="group-image" src=${message.text[i].data.url} referrerpolicy="no-referrer">`
            }


            else if (message.text[i].type == "face") {
                message_html += `<img src="./src/faces/${message.text[i].data.id}.png" width="24px" referrerpolicy="no-referrer">`
            }


            else if (message.text[i].type == "json") {
                let json_card_info = JSON.parse(message.text[i].data.data);
                message_html += `    <div class="json-card">
        <img src="${json_card_info.meta.detail_1.icon}" width="16px">
        <span class="json-card-app-name">${json_card_info.meta.detail_1.title}</span>
        <div class="json-card-desc">${json_card_info.meta.detail_1.desc}</div>
        <img class="json-card-preview" src="https://${json_card_info.meta.detail_1.preview}" referrerpolicy="no-referrer" width="250px">
    </div>`;
            }

            else if (message.text[i].type == "file") {
                message_html += `    <div class="json-card">
        <span class="json-card-app-name">此文件以保存到晶格内网。</span>
        <div>${message.text[i].data.file}<br><br>${Helper.DisplayFileSize(parseInt(message.text[i].data.file_size))}</div>
        <img class="json-card-preview" src="" referrerpolicy="no-referrer" width="250px">
    </div>`;
            }

            else if (message.text[i].type == 'reply'){
                // 回复消息只支持引用部分的text，image，face以及json/forward的消息提示
                console.log("reply mesg");
                message_html += `<div class="replybox">`;
                let quoteMsg = GetMessage (message.text[i].data.id);
                message_html += `<div>
                <img src="${quoteMsg.avatar}" alt="avatar" style="width: 16px; height: 16px; border-radius: 16px;">`;
                message_html += `<span style="padding-left: 10px; font-size: 14px; position: relative; top: -3px">${quoteMsg.username}</span>
                </div>`;
                for (let i = 0; i < quoteMsg.text.length; i++) {
                    if (quoteMsg.text[i].type == "text") {
                        message_html += quoteMsg.text[i].data.text
                    }
                    else if (quoteMsg.text[i].type == "image") {
                        message_html += `<img id="group-image" src=${quoteMsg.text[i].data.url} referrerpolicy="no-referrer">`
                    }
                    else if (quoteMsg.text[i].type == "face") {
                        message_html += `<img src="./src/faces/${quoteMsg.text[i].data.id}.png" width="24px" referrerpolicy="no-referrer">`
                    }
                    else if (quoteMsg.text[i].type == "json") {
                        message_html += "[JSON卡片]";
                    }
                    else if (quoteMsg.text[i].type == "forward"){
                        message_html += "[合并转发] 聊天记录";
                    }
                    else if (quoteMsg.text[i].type == "file"){
                        message_html += "[文件] " + quoteMsg.text[i].data.file;
                    }
                    else
                    {
                        message_html += quoteMsg.text[i].type;
                    }
                    
                };
                message_html += `</div>`;
            };


            if (message.text[i].type == 'forward') {
                let forward_info = message.text[i].data.content;
                let message_content = "";
                for (let i = 0; i < 4 && i < forward_info.length; i++) {
                    if (!('sender' in forward_info[i])) {
                        forward_info[i].sender = { card: "User" };
                    }
                    message_content += `<div class="single-line" style="max-width: 200px; opacity: 0.8"; padding: 5px 10px; padding-left: 20px>` + (forward_info[i].sender.card || forward_info[i].sender.nickname || "User") + ": " + forward_info[i].raw_message + "\n" + `</div>`;
                }
                message_html += `
                    <div class="forward-card">
                        <span class="json-card-app-name">合并转发 | ${forward_info[0].message_type}</span>
                        <div class="json-card-desc">${message_content}<div style="opacity: 0.5; margin-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 5px">查看 ${forward_info.length} 条转发消息</div></div>
                    </div>`;
            }



    };
    
    const messageElement = document.createElement('div');
    messageElement.className = (message.user_id == self_id) ? 'message-item-self' : 'message-item';
    messageElement.innerHTML = `
    <img class="avatar" src="${message.avatar}" width="24" height="24">
    <div class="message-text">${message_html}</div>`
    messagesContainer.appendChild(messageElement);
    if (isScrolledToBottom) {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };
    }
    else {
        console.error('无法找到 messages 容器');
    }
}
function GetMessage (id){
    const messages = message_list[currentGroupId] || [];
    for (let i = 0; i < messages.length; i++){
        if (messages[i].id == id){
            return messages[i];
        }
    }
    return {text: [{type: 'text', data: {text: '引用消息不存在'}}]};
}
document.addEventListener('DOMContentLoaded', function() {
    const connectStatus = document.querySelector('.connect-status');
    const statusBar = document.querySelector('.status-bar');

    connectStatus.addEventListener('mouseenter', function() {
        statusBar.style.display = 'block';
    });

    connectStatus.addEventListener('mouseleave', function() {
        statusBar.style.display = 'none';
    });

    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('sendButton');
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});

