// HTTP API以及WS API的调用
export class API{
    constructor(httpUrl, wsObj) {
        this.httpUrl = httpUrl;
        this.ws = wsObj;
    };
    SendGroupMessage(group_id, message) {
        fetch(this.httpUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ group_id: group_id, message: msg, user_id: 1 }),
        })
        .then(response => response.json())
        .then(data => {console.log('API响应:', data); return data;})
        .catch(error => console.error('API错误:', error));
    };
    GetGroupInfo(group_id){
        this.ws.send(JSON.stringify({
            action: "get_group_info",
            params: {
                group_id: group_id,
                no_cache: true
            }
        }))
    };
    async SendGroupMessageHTTP(group_id, user_id, msg) {
        try {
            const response = await fetch(this.httpUrl + "/send_group_msg", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ group_id: group_id, message: msg, user_id: user_id }),
            });
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            const data = await response.json();
            console.log('API响应:', data);
            return data;
        } catch (error) {
            console.error('API错误:', error);
            throw error;
        }
    }
    async getGroupListHTTP() {
        try {
            const response = await fetch(this.httpUrl + "/get_group_list", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: { data: null },
            });
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            const data = await response.json();
            console.log('API响应:', data);
            return data;
        } catch (error) {
            console.error('API错误:', error);
            throw error;
        }
    }
};