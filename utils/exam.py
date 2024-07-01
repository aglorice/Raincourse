import time

from rich.console import Console
import re
from api.api import RainAPI
from config import DO_WORK_DURATION_SPAN
from utils.utils import is_exist_answer_file, jsonFileToDate


def find_answer(question_id, console: Console, answer) -> dict:
    for key, value in enumerate(answer['answer']['data']['problem_results']):
        if value['problem_id'] == question_id:
            return value
    return {}


def fetch_answer_from_file(console: Console, exam_id) -> dict:
    console.log(f"拉取答案文件 {exam_id}.json")
    _answer = {}
    if is_exist_answer_file(exam_id + ".json"):
        _answer = jsonFileToDate(exam_id+".json")
        console.log(f"读取答案文件成功 {exam_id}.json")
        return _answer
    else:
        console.log(f"答案文件不存在 {exam_id}.json")
        console.log(f"退出答题")
        return {}


def construct_answer_formation(question: dict, console: Console, other_answer) -> list:
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
    else:
        console.log(f"还没有实现 {question['TypeText']} 类的题型")

    console.log(f"匹配答案成功 ===> {result}")
    answer = [{"problem_id": question['ProblemID'], "result": result, "time": timestamp_milliseconds}]
    return answer


def do_work(console: Console, rain: RainAPI, cache_work, all_question, exam_id) -> None:
    re_cord = [item['problem_id'] for item in cache_work['data']['results']]
    # 从文件中读取答案
    _answer = fetch_answer_from_file(exam_id=exam_id, console=console)
    if _answer == {}:
        return
    console.log(f"开始答题")
    for index, question in enumerate(all_question['data']['problems']):
        pattern = re.compile(r'<[^>]+>', re.S)
        title = pattern.sub('', question['Body']).replace('\n', '')

        console.log(
            f"拉取题目成功：(id: {question['ProblemID']})[{question['TypeText']}][{title}]({question['Score']} 分)"
        )
        answer = construct_answer_formation(question, console, _answer)

        if question['ProblemID'] in re_cord:
            res = rain.post_test(exam_id, re_cord, answer)
        else:
            res = rain.post_test(exam_id, re_cord, answer)
            re_cord.append(question['ProblemID'])
        if res['errcode'] == 0:
            console.log(f"答案保存成功：{res}")
        time.sleep(DO_WORK_DURATION_SPAN)
