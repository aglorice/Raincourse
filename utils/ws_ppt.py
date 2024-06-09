import time

import websocket
import json
import threading


class WebSocketClient_PPT:
    def __init__(self, uri, header, console, class_id, cards_id, page_count):
        self.uri = uri
        self.ws = None
        self.running = True
        self.qr_code_timer = None

        self.header = header

        self.console = console
        self.class_id = class_id
        self.cards_id = cards_id
        self.page_count = page_count

        self.data = []

    def on_message(self, ws, message):
        response = json.loads(message)
        if "正确" == response.get("errmsg", ""):
            self.console.log(f"[green]完成ppt浏览")
            self.stop()
        self.console.log(f"[green]Received message: {response}")
        self.request_view_record()
        self.request_view_record_answer()

    def request_view_record_answer(self):
        if not self.running:
            return
        message = {
            "op": "view_record_answer",
            "cardsID": self.class_id,
            "type": "page",
            "platform": "web",
        }
        self.ws.send(json.dumps(message))

    def on_error(self, ws, error):
        self.console.log(f"[red]Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.console.log("[blue]Connection closed")

    def on_open(self, ws):
        pass

    def request_view_record(self):
        if not self.running:
            return
        timestamp_seconds = time.time()
        # 转换为毫秒级时间戳
        timestamp_milliseconds = int(timestamp_seconds * 1)
        message = {
            "op": "view_record",
            "cardsID": self.class_id,
            "type": "cache",
            "data": self.page_count * [1],
            "start_time": timestamp_milliseconds,
            "platform": "web",
            "user_id": self.cards_id,
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
