import os
import time
from rich.console import Console

from api.api import RainAPI
from config import PPT_DURATION_SPAN
from utils.exam import do_work
from utils.ui import show_menu, show_course, show_works, show_all_answer_file, show_ppt

from utils.utils import dateToJsonFile, jsonFileToDate, is_exist_answer_file


def select_menu(console: Console, rain: RainAPI) -> None:
    while True:
        show_menu(console)
        choose = console.input("请选择你要选择的功能: ")
        # 查看课程
        if choose == "1":
            res = rain.get_course_list()
            show_course(res['data']['list'], console)
        # 查看作业
        elif choose == "2":
            res = rain.get_course_list()

            show_course(res['data']['list'], console)
            index = console.input("请输入你要选择的课程: ")
            course_id = res['data']['list'][int(index) - 1]['classroom_id']

            res = rain.get_work(course_id)['data']['activities']
            show_works(res, console)
        elif choose == "3":
            res = rain.get_course_list()

            show_course(res['data']['list'], console)

            index = console.input("请输入你要选择的课程: ")
            course_id = res['data']['list'][int(index) - 1]['classroom_id']

            res = rain.get_work(course_id)['data']['activities']

            show_works(res, console)
            index = console.input("请输入你要选择的作业: ")
            work_id = res[int(index) - 1]['courseware_id']

            work_name = res[int(index) - 1]['title']
            res = rain.get_token_work(course_id, work_id)

            # 根据获取的token进入考试
            rain.get_exam_work_token(work_id, res['data']['user_id'], res['data']['token'], 'zh')

            res = rain.get_all_answer(work_id)
            if res is None:
                console.log("获取题目失败,请检查是否可以查看试卷")
                continue
            dateToJsonFile(res, {"exam_id": work_id, "exam_name": work_name, "exam_type": "考试试题"})
            console.log(f"保存答案成功：/answer/{work_id}.json")
        elif choose == "4":
            res = rain.get_course_list()

            show_course(res['data']['list'], console)
            index = console.input("请输入你要选择的课程: ")
            course_id = res['data']['list'][int(index) - 1]['classroom_id']

            res = rain.get_work(course_id)['data']['activities']
            show_works(res, console)
            index = console.input("请输入你要选择的作业: ")
            work_id = res[int(index) - 1]['courseware_id']

            # 获取考试的token
            res = rain.get_token_work(course_id, work_id)

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
            res = rain.get_course_list()

            show_course(res['data']['list'], console)
            index = console.input("请输入你要选择的课程: ")
            course_id = res['data']['list'][int(index) - 1]['classroom_id']

            res = rain.get_ppt(course_id)
            show_ppt(res['data']['activities'], console)
            console.log(f"获取用户信息", style="bold green")
            user_info = rain.get_user_info()
            console.log(user_info)

            for index,ppt in enumerate(res['data']['activities']):
                if not is_exist_answer_file(ppt['courseware_id'] + ".json"):
                    flag = console.input(
                        f"[red]答案文件不存在 {ppt['title']},是否从当前账号获取答案并保存到文件中 {ppt['title']},确定请输入任意键，退出请输入q: [red]")
                    if flag == "q":
                        return
                    ppt_questions = rain.get_ppt_questions_answer(course_id, ppt['courseware_id'])
                    dateToJsonFile(ppt_questions, {"exam_id": ppt['courseware_id'], "exam_name": ppt['title'],
                                                   "exam_type": "课件试题"})
                    console.log(f"保存答案成功：/answer/ppt{['courseware_id']}.json")
                    continue
                console.log(f"答案文件存在 {ppt['title']}", style="bold green")
                ppt_questions_answer = jsonFileToDate(f"{ppt['courseware_id']}.json")

                for question in ppt_questions_answer['answer']['data']['problem_results']:
                    # 这里只做了选择和填空的适配
                    console.log(f"开始做题。。", style="bold green")
                    result = question['answer']
                    # 选择题
                    if ";" in question['answer']:
                        # 将字符串分割成单独的信号
                        item = question['answer'].split(";")
                        # 为每个信号分配一个唯一的编号
                        result = {index + 1: signal for index, signal in enumerate(item)}
                    # 填空题

                    res = rain.post_ppt_answer(course_id, question['id'], result)
                    if res['errcode'] != 0:
                        console.log(f"提交答案失败: {res['errmsg']}（这里只做了选择题，填空题没做😶‍🌫️）", style="bold red")
                        continue
                    console.log(f"提交答案成功: Answer:{res['data']['answer']} Result:{res['data']['correct']}, Score:{res['data']['score']}", style="bold green")

                console.log(f"开始浏览ppt: {ppt['title']}", style="bold green")
                rain.view_ppt(ppt['courseware_id'], user_info['data'][0]["user_id"], ppt['count'])
                time.sleep(PPT_DURATION_SPAN)

        elif choose == "7":
            return
        else:
            console.print("输入错误，请重新输入")
            select_menu(console, rain)
        choose = console.input("继续选择请输入任意键,退出请输入q:  ")
        if choose == "q":
            break
