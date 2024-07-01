import json
import os


def dateToJsonFile(answer: list, info: dict) -> None:
    """
    将答案写入文件保存为json格式
    :param answer:
    :param info:
    :return:
    """
    to_dict = {
        "answer": answer,
        "info": info
    }
    # json.dumps 序列化时对中文默认使用的ascii编码.想输出真正的中文需要指定ensure_ascii=False
    json_data = json.dumps(to_dict, ensure_ascii=False)
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.join(path, "answer", f"{info['exam_id']}.json")
    with open(path, 'w', encoding="utf-8") as f_:
        f_.write(json_data)


def jsonFileToDate(file_name) -> dict:
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    file = os.path.join(path, "answer", f"{file_name}")
    with open(file, 'r', encoding="utf-8") as f_:
        json_data = dict(json.loads(f_.read()))
    return json_data


def is_exist_answer_file(work_file_name: str) -> bool:
    answer_files = []
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.join(dir_path, "answer")
    for root, dirs, files in os.walk(path):
        answer_files.append(files)
    if work_file_name in answer_files[0]:
        return True
    else:
        return False


