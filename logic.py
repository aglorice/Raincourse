
import os

import time

from rich.console import Group, Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from api.api import RainAPI
from utils.utils import dateToJsonFile, jsonFileToDate, is_exist_answer_file


def show_menu(console: Console) -> None:
    console.print(Panel(
        title="[green]菜单",
        renderable=
        Group(
            Text("1.查看课程", justify="center", style="bold yellow"),
            Text("2.查看试题", justify="center", style="bold yellow"),
            Text("3.导出试题", justify="center", style="bold yellow"),
            Text("4.自动答题", justify="center", style="bold yellow"),
            Text("5.答案文件", justify="center", style="bold yellow"),
            Text("6.退出登录", justify="center", style="bold yellow"),
        ),
        style="bold green",
        width=120,
    ))


def show_course(courses: list, console: Console) -> None:
    tb = Table("序号", "课程id", "课程名", "老师名", border_style="blue", width=116)

    for index, course in enumerate(courses):
        _course = course["course"]
        tb.add_row(
            str(index + 1),
            f"[green]{_course['id']}[/green]",
            _course["name"],
            course["teacher"]['name'],
            style="bold yellow"
        )
    console.print(
        Panel(
            title="[blue]课程信息[/blue]",
            renderable=tb,
            style="bold green",
        )
    )


def show_works(works: list, console: Console) -> None:
    status = {
        0: "未提交",
        1: "[red]未提交[red]",
        2: "已批改",
        3: "[green]已批改[green]",
    }
    tb = Table("id", "作业id", "作业名称", "作业状态", "分数", "题目数量", border_style="blue", width=116)
    for index, work in enumerate(works):
        tb.add_row(
            str(index + 1),
            f"[green]{work['courseware_id']}[/green]",
            work['title'],
            status[work['status']],
            str(work["score"]),
            str(work["problem_count"]),
            style="bold yellow"
        )
    console.print(
        Panel(
            title="[blue]作业信息",
            renderable=tb,
            style="bold green",
        )
    )


def find_answer(question_id, console: Console, other_answer) -> dict:
    for key, value in enumerate(other_answer['answer']['data']['problem_results']):
        if value['problem_id'] == question_id:
            return value
    return {}


def create_answer(question: dict, console: Console, other_answer) -> list:
    console.log(f"匹配答案...")
    timestamp_seconds = time.time()
    # 转换为毫秒级时间戳
    timestamp_milliseconds = int(timestamp_seconds * 1000)
    result = []
    answer = find_answer(question['ProblemID'], console, other_answer)
    if answer == {}:
        console.log(f"未找到答案 {question['ProblemID']}")

    if question['TypeText'] == "单选题":
        result = answer['answer']
    elif question['TypeText'] == "填空题":
        _result = answer['answer']
        result = {}
        for key, value in _result.items():
            result[key] = value[0]
    console.log(f"匹配答案成功 ===> {result}")
    answer = [{"problem_id": question['ProblemID'], "result": result, "time": timestamp_milliseconds}]
    return answer


def do_work(console: Console, rain: RainAPI, cache_work, all_question, exam_id) -> None:
    re_cord = [item['problem_id'] for item in cache_work['data']['results']]
    console.log(f"拉取答案文件 {exam_id}.json")
    _answer = {}
    if is_exist_answer_file(exam_id):
        _answer = jsonFileToDate(exam_id)
        console.log(f"读取答案文件成功 {exam_id}.json")
    else:
        console.log(f"答案文件不存在 {exam_id}.json")
        console.log(f"退出答题")
        return

    console.log(f"开始答题")
    for index, question in enumerate(all_question['data']['problems']):

        import re

        pattern = re.compile(r'<[^>]+>', re.S)
        title = pattern.sub('', question['Body']).replace('\n', '')

        console.log(
            f"拉取题目成功：(id: {question['ProblemID']})[{question['TypeText']}][{title}]({question['Score']} 分)")

        answer = create_answer(question, console, _answer)

        if question['ProblemID'] in re_cord:

            res = rain.post_test(exam_id, re_cord, answer)
        else:

            res = rain.post_test(exam_id, re_cord, answer)
            re_cord.append(question['ProblemID'])

        if res['errcode'] == 0:
            console.log(f"答案保存成功：{res}")


def select_menu(console: Console, rain: RainAPI) -> None:
    while True:

        show_menu(console)
        choose = console.input("请选择你要选择的功能: ")
        if choose == "1":
            res = rain.get_course_list()
            show_course(res['data']['list'], console)
        elif choose == "2":
            res = rain.get_course_list()

            show_course(res['data']['list'], console)
            index = console.input("请输入你要选择的课程: ")
            course_id = res['data']['list'][int(index) - 1]['classroom_id']

            res = rain.get_test(course_id)['data']['activities']
            show_works(res, console)
        elif choose == "3":
            res = rain.get_course_list()

            show_course(res['data']['list'], console)
            index = console.input("请输入你要选择的课程: ")
            course_id = res['data']['list'][int(index) - 1]['classroom_id']

            res = rain.get_test(course_id)['data']['activities']

            show_works(res, console)
            index = console.input("请输入你要选择的作业: ")
            work_id = res[int(index) - 1]['courseware_id']

            work_name = res[int(index) - 1]['title']
            res = rain.get_token_work(course_id, work_id)

            # 返回结果(res)
            # {'msg': '', 'status': 200, 'data': {'token':
            # 'T+L7vjn+64rrR98bJ+sR3rXrdsWfLArXpvxq6BuewNYeTZWvq3kmzgxNXRsDvkSjzyRXbxRDNJu9U6PstllbUQ==', 'user_id':
            # 52480345}, 'success': True}

            # 根据获取的token进入考试
            rain.get_exam_work_token(work_id, res['data']['user_id'], res['data']['token'], 'zh')

            res = rain.get_all_answer(work_id)
            if res == None:
                console.log("获取题目失败,请检查是否可以查看试卷")
                continue
            dateToJsonFile(res, {"exam_id": work_id, "exam_name": work_name})
            console.log(f"保存答案成功：/answer/{work_id}.json")
        elif choose == "4":
            res = rain.get_course_list()

            show_course(res['data']['list'], console)
            index = console.input("请输入你要选择的课程: ")
            course_id = res['data']['list'][int(index) - 1]['classroom_id']

            res = rain.get_test(course_id)['data']['activities']
            show_works(res, console)
            index = console.input("请输入你要选择的作业: ")
            work_id = res[int(index) - 1]['courseware_id']
            # 获取token
            res = rain.get_token_work(course_id, work_id)

            # 返回结果(res)
            # {'msg': '', 'status': 200, 'data': {'token':
            # 'T+L7vjn+64rrR98bJ+sR3rXrdsWfLArXpvxq6BuewNYeTZWvq3kmzgxNXRsDvkSjzyRXbxRDNJu9U6PstllbUQ==', 'user_id':
            # 52480345}, 'success': True}

            # 根据获取的token进入考试
            rain.get_exam_work_token(work_id, res['data']['user_id'], res['data']['token'], 'zh')
            console.log("获取已完成的问题")
            cache_work = rain.get_cache_work(work_id)

            console.log("获取全部的试题")
            all_question = rain.get_all_question(work_id)

            try:
                do_work(console, rain, cache_work, all_question, work_id)
            except KeyError as e:
                console.log(f"获取题目失败,请检查是否已经提交，如果还未·开始答题，请在手机端先点击开始答题 :{e}")
                continue
        elif choose == "5":
            show_all_answer_file(console)

        elif choose == "6":
            return
        else:
            console.print("输入错误，请重新输入")
            select_menu(console, rain)
        choose = console.input("继续选择请输入任意键,退出请输入q:  ")
        if choose == "q":
            break


def show_all_answer_file(console: Console) -> None:
    answer_files = []
    answer_file_info = []
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "answer")

    for root, dirs, files in os.walk(path):
        answer_files.append(files)
    for item in answer_files[0]:
        _path = os.path.join(path, item)
        answer_file_info.append(jsonFileToDate(_path)["info"])

    tb = Table("id", "作业名", "文件名称", border_style="blue", width=116)
    for work_info in answer_file_info:
        tb.add_row(
            f"[green]{work_info['exam_id']}[/green]",
            work_info["exam_name"],
            work_info["exam_id"] + ".json",
            style="bold yellow"
        )
    console.print(
        Panel(
            title="[blue]作业文件列表[/blue]",
            renderable=tb,
            style="bold green",
        )
    )
