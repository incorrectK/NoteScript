from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests


FORWORD_PORT = 28080
ECHO_PORT = 38080
BURP_PORT = 8080


class ForwardRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('content-length', 0))

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        data = self.rfile.read(content_length)
        if str(self.path) == "/request":
            r = requests.request('REQUEST', 'http://127.0.0.1:{}/'.format(ECHO_PORT),
                                 proxies={'http': 'http://127.0.0.1:{}'.format(BURP_PORT)},
                                 data=data)
            new_data = r.text
            self.wfile.write(new_data.encode('utf8'))
        else:
            try:
                r = requests.request('RESPONSE', 'http://127.0.0.1:{}/'.format(ECHO_PORT),
                                     proxies={'http': 'http://127.0.0.1:{}'.format(BURP_PORT)},
                                     data=data)
                new_data = r.text
                self.wfile.write(new_data.encode('utf8'))
            except:
                self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'content-type')

        self.send_header('Allow', 'POST,OPTIONS')
        self.end_headers()



class RequestHandler(BaseHTTPRequestHandler):
    def do_REQUEST(self):
        content_length = int(self.headers.get('content-length', 0))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.rfile.read(content_length))

    do_RESPONSE = do_REQUEST


def echo_server_thread():
    print('>开始监听镜像服务器,端口:{}'.format(ECHO_PORT))
    server = HTTPServer(('', ECHO_PORT), RequestHandler)
    server.serve_forever()


def echo_forward_server_thread():
    print('>开始监听转发服务器,端口:{}'.format(FORWORD_PORT))
    server = HTTPServer(('', FORWORD_PORT), ForwardRequestHandler)
    server.serve_forever()


def get_payload():
    print("============================================================================================")
    print('''
        var xhr = new XMLHttpRequest();
        xhr.open('post', 'http://ip:28080/request', false);
        xhr.setRequestHeader("Content-type", "application/json;charset=UTF-8");
        xhr.send(JSON.stringify(n));
        let modify_data = JSON.parse(xhr.responseText);
        n = modify_data;
    ''')

    '''
    var xhr = new XMLHttpRequest();
    xhr.open('post', 'http://192.168.0.100:28080/request', false);
    xhr.setRequestHeader("Content-type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(n));
    let modify_data = JSON.parse(xhr.responseText);
    n = modify_data;
    '''

    print("============================================================================================")

    '''
    uni.request({
    url: 'https://www.example.com/request', //仅为示例，并非真实接口地址。
    method: 'POST',
    data: {
        text: 'uni.request'
    },
    header: {
        'Content-type': 'application/json;charset=UTF-8' //自定义请求头信息
    },
    success: (res) => {
        console.log(res.data);
        this.text = 'request success';
        let modify_data = JSON.parse(res.data);
        “明文数据参数” = modify_data;
    }
});
    '''

if __name__ == '__main__':
    get_payload()
    t1 = Thread(target=echo_forward_server_thread)
    t = Thread(target=echo_server_thread)
    t.daemon = True
    t.start()
    t1.daemon = True
    t1.start()
    print(">请启动Burp,端口:8080")
    for t in [t, t1]:
        t.join()