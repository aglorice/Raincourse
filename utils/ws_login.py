import websocket
import json
import threading




class WebSocketClient:
    def __init__(self, uri, header, console, callback):
        self.uri = uri
        self.ws = None
        self.running = True
        self.qr_code_timer = None

        self.header = header

        self.console = console
        self.callback = callback

    def on_message(self, ws, message):
        response = json.loads(message)
        if 'qrcode' in response:
            self.console.log("[yellow]请扫描二维码")
            from qrcode import QRCode
            qr = QRCode()
            qr.add_data(response['qrcode'])
            qr.print_ascii(invert=True)
            # 每隔60秒更换一次二维码
            if self.qr_code_timer:
                self.qr_code_timer.cancel()
            self.qr_code_timer = threading.Timer(60, self.request_qr_code)
            self.qr_code_timer.start()
        elif 'subscribe_status' in response and response['subscribe_status'] == True:
            self.console.log(
                f"[green]登录成功！ 姓名：{response['Name']}，学校：{response['School']}，上次登录ip：{response['LastLoginIP']}")
            self.stop()
            self.callback(response['UserID'], response['Auth'])

    def on_error(self, ws, error):
        self.console.log(f"[red]Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.console.log("[blue]Connection closed")

    def on_open(self, ws):
        self.request_qr_code()  # 初次请求二维码

    def request_qr_code(self):
        if not self.running:
            return
        message = {
            "op": "requestlogin",
            "role": "web",
            "version": 1.4,
            "type": "qrcode",
            "from": "web"
        }
        self.ws.send(json.dumps(message))

    def start(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.uri,
                                         header=self.header,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

    def stop(self):
        self.running = False
        if self.qr_code_timer:
            self.qr_code_timer.cancel()
        if self.ws:
            self.ws.close()
