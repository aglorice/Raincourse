import json
import time
from functools import cache

import requests

from utils.ws_login import WebSocketClient
from utils.ws_ppt import WebSocketClient_PPT


class RainAPI:
    def __init__(self, console):
        self.sees = requests.Session()
        self.ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/58.0.3029.110 Safari/537.3")

        self.console = console

        self.init()

    def init(self):
        url = "https://www.yuketang.cn/web"

        res = self.sees.get(url, headers={"User-Agent": self.ua})
        if res.status_code == 200:
            self.console.log("[green]网站初始化访问成功[/green]")
        else:
            self.console.log("[red]网站初始化访问失败[/red]")

    def login(self):
        """websocket登录"""
        self.console.log("[green]开始登录[/green]")
        uri = "wss://www.yuketang.cn/wsapp/"
        client = WebSocketClient(uri, self.sees.headers, self.console, self.get_token)
        try:
            client.start()
        except KeyboardInterrupt:
            self.console.log("[red]用户中断[/red]")
            client.stop()

    def get_token(self, user_id, auth):
        url = "https://www.yuketang.cn/pc/web_login"
        res = self.sees.post(url, data=json.dumps({"UserID": user_id, "Auth": auth}))
        if res.status_code == 200:
            self.console.log("[green]获取登录凭证成功[/green]")
        else:
            self.console.log("[red]获取登录凭证失败[/red]")

    def get_user_info(self):
        """
        获取用户信息
        :return:
        """
        url = "https://www.yuketang.cn/v2/api/web/userinfo"
        headers = {
            "User-Agent": self.ua,
            "Referer": "https://www.yuketang.cn/",
        }
        response = self.sees.get(url, headers=headers)
        return response.json()

    @cache
    def get_course_list(self):
        """
        获取课程列表
        :return:
        """
        url = "https://www.yuketang.cn/v2/api/web/courses/list?identity=2"
        headers = {
            "User-Agent": self.ua,
            "Referer": "https://www.yuketang.cn/",
        }
        response = self.sees.get(url, headers=headers)
        return response.json()

    def get_test(self, course_id):
        """
        获取课程测试题
        :return:
        """
        url = f"https://www.yuketang.cn/v2/api/web/logs/learn/{course_id}?actype=5&page=0&offset=20&sort=-1"
        headers = {
            "User-Agent": self.ua,
            "Referer": "https://www.yuketang.cn/",
        }
        response = self.sees.get(url, headers=headers)
        return response.json()

    def post_test(self, exam_id: str, record: list, answer):
        """
        提交测试题
        :return:
        """
        url = f"https://examination.xuetangx.com/exam_room/answer_problem"
        headers = {
            "User-Agent": self.ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, zstd",
            "Content-Type": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Origin": "https://examination.xuetangx.com",
            "Pragma": "no-cache",
            "Referer": f"https://examination.xuetangx.com/exam/{exam_id}?isFrom=2",
            "Sec-Ch-Ua": "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Client": "web",
            "Xtbz": "cloud"
        }

        data = {
            "results": answer,
            "exam_id": int(exam_id),
            "record": record
        }
        # Use json parameter to pass JSON data
        response = self.sees.post(url, headers=headers, json=data)
        # 设置响应编码为 UTF-8
        response.encoding = 'utf-8'
        return response.json()

    def get_all_answer(self, exam_id):
        url = f"https://examination.xuetangx.com/exam_room/problem_results?exam_id={exam_id}"

        headers = {
            "User-Agent": self.ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, zstd",
            "Content-Type": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Origin": "https://examination.xuetangx.com",
            "Pragma": "no-cache",
            "Referer": f"https://examination.xuetangx.com/exam/{exam_id}?isFrom=2",
            "Sec-Ch-Ua": "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Client": "web",
            "Xtbz": "cloud"
        }

        response = self.sees.get(url, headers=headers)
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            return None

    def get_all_question(self, exam_id):
        """
        获取所有测试题
        :return:
        """
        url = f"https://examination.xuetangx.com/exam_room/show_paper?exam_id={exam_id}"
        headers = {
            "User-Agent": self.ua,
            "Referer": "https://www.yuketang.cn/",
        }
        response = self.sees.get(url, headers=headers)

        return response.json()

    def get_cache_work(self, work_id):
        url = f"https://examination.xuetangx.com/exam_room/cache_results?exam_id={work_id}"
        headers = {
            "User-Agent": self.ua,
            "Referer": "https://www.yuketang.cn/",
        }
        response = self.sees.get(url, headers=headers)
        return response.json()

    def init_exam(self, course_id, work_id):
        url = f"https://www.yuketang.cn/v2/web/trans/{course_id}/{work_id}?status=1"
        headers = {
            "User-Agent": self.ua,
            "Referer": "https://www.yuketang.cn/",
        }

        response = self.sees.get(url, headers=headers, allow_redirects=True)

        if response.status_code == 200:
            self.console.log("[green]初始化测试题成功[/green]")
        else:
            self.console.log("[red]初始化测试题失败[/red]")

    def get_token_work(self, course_id, work_id):
        url = f"https://www.yuketang.cn/v/exam/gen_token"
        headers = {
            "User-Agent": self.ua,
            "Referer": f"https://www.yuketang.cn/v2/web/trans/{course_id}/{work_id}?status=1",
            "X-Csrftoken": self.sees.cookies.get("csrftoken"),
        }
        response = self.sees.post(url, headers=headers,
                                  data=json.dumps({"exam_id": work_id, "classroom_id": str(course_id)}))
        return response.json()

    def get_exam_work_token(self, work_id, user_id, token, language):
        """
        获取测试题token
        :param work_id:
        :param user_id:
        :param token:
        :param language:
        :return:
        """
        url = f"https://examination.xuetangx.com/login"
        headers = {
            "User-Agent": self.ua,
        }
        res = self.sees.get(url, headers=headers, params={"exam_id": work_id, "user_id": user_id, "crypt": token,
                                                          "next": f"https://examination.xuetangx.com/exam/{work_id}?isFrom=2",
                                                          "language": language}, allow_redirects=True)
        if res.status_code == 200:
            self.console.log("[green]获取测试题token成功[/green]")
        else:
            self.console.log("[red]获取测试题token失败[/red]")

    def view_ppt(self, class_id, user_id, page_count):

        self.console.log("[green]开始浏览ppt[/green]")
        uri = "wss://www.yuketang.cn/ws/"
        client = WebSocketClient_PPT(uri, self.get_session_headers(class_id), self.console, class_id, user_id,
                                     page_count)
        try:
            client.start()
        except KeyboardInterrupt:
            self.console.log("[red]用户中断[/red]")
            client.stop()

    def get_ppt(self, class_id):
        url = f"https://www.yuketang.cn/v2/api/web/logs/learn/{class_id}?actype=15&page=0&offset=200&sort=-1"
        headers = {
            "User-Agent": self.ua,
        }
        response = self.sees.get(url, headers=headers)
        return response.json()

    def get_session_headers(self, class_id):
        headers = {}
        # Copy the session headers
        headers.update(self.sees.headers)
        headers['User-Agent'] = self.ua
        headers['X-Csrftoken'] = self.sees.cookies.get("csrftoken")

        # Add the cookies to the headers
        cookies = self.sees.cookies.get_dict()
        cookie_header = '; '.join([f"{name}={value}" for name, value in cookies.items()])
        cookie_header += f"; classroomId=;{class_id}"
        if cookie_header:
            headers['Cookie'] = cookie_header

        return [f"{name}: {value}" for name, value in headers.items()]

    def get_ppt_questions_answer(self, class_id, ppt_id):

        url = f"https://www.yuketang.cn/v2/api/web/cards/detlist/{ppt_id}?classroom_id={class_id}"
        headers = {
            "User-Agent": self.ua,
        }
        response = self.sees.get(url, headers=headers)
        return response.json()

    def post_ppt_answer(self, class_id, answer_id, answer_content):
        url = "https://www.yuketang.cn/v2/api/web/cards/problem_result"
        headers = {
            "User-Agent": self.ua,
            "X-Csrftoken": self.sees.cookies.get("csrftoken"),
            "Sec-Ch-Ua": "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Cookie": f"classroom_id={class_id};classroomId={class_id};sessionid={self.sees.cookies.get('sessionid')}",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Client": "web",
            "Xtbz": "ykt",
            "Classroom-Id": str(class_id),
            "Content-Type": "application/json;charset=UTF-8",
            "Cache-Control": "no-cache",
            "Origin": "https://www.yuketang.cn",
            "Pragma": "no-cache"
        }

        data = {
            "cards_problem_id": answer_id,
            "classroom_id": str(class_id),
            "duration": 12,
            "result": answer_content,
        }

        response = self.sees.post(url, headers=headers, data=json.dumps(data))
        return response.json()


    def check_ppt_answer(self, class_id):
        # 加了这个请求就能100%
        url = f"https://www.yuketang.cn/v2/api/web/classrooms_role?classroom_id={class_id}"
        headers = {
            "User-Agent": self.ua,
        }
        response = self.sees.get(url, headers=headers)
        return response.json()
