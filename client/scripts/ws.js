// 控制WebSocket的连接和重连以及connect-status的状态显示
export class WSMessage {
    constructor(wsUri, onmessage_handler) {
        this.wsUri = wsUri;
        this.onmessage_handler = onmessage_handler;
        this.websocket = new WebSocket(wsUri);
        this.setWSEvent();
        this.websocket.onopen = function() {
            document.getElementsByClassName("ws-status")[0].innerText = "OneBot.Chat.Debug · Online";
            document.getElementsByClassName("circle-green")[0].id = "circle-green";
            console.log('WebSocket连接已建立');
        };
    };
    
    ProcessWSError(error) {
        document.getElementsByClassName("ws-status")[0].innerText = "OneBot.Chat.Debug · Error";
        document.getElementsByClassName("circle-green")[0].id = "circle-red";
        console.error('WebSocket错误:', error);
    };

    process_WS_close() {
        document.getElementsByClassName("ws-status")[0].innerText = "OneBot.Chat.Debug · Reconnecting";
        document.getElementsByClassName("circle-green")[0].id = "circle-red";
        console.log('WebSocket连接断开，5秒后重连');
        this.reconnectInterval = setInterval(() => {
            console.log('尝试重新连接WebSocket...');
            this.websocket = new WebSocket(this.wsUri);
    
            this.websocket.onopen = () => {
                clearInterval(this.reconnectInterval);
                document.getElementsByClassName("ws-status")[0].innerText = "OneBot.Chat.Debug · Online";
                document.getElementsByClassName("circle-green")[0].id = "circle-green";
                console.log('WebSocket重新连接成功');
                this.setWSEvent();
            };
        }, 5000);
    }
    
    setWSEvent() {
        this.websocket.onmessage = (event) => {
            this.onmessage_handler(event);
        };
        this.websocket.onerror = (error) => {
            this.ProcessWSError(error);
        };
        this.websocket.onclose = () => {
            this.process_WS_close();
        };
    }
    send(data) {
        this.websocket.send(data);
    }
}
