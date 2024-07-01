import os
from config import __VERSION__


def git_tag():
    os.system("git tag -a {} -m '{}'".format(__VERSION__, __VERSION__))
    os.system("git push origin {}".format(__VERSION__))
    print("3.自动生成创建新git tag标签，并上穿到github成功！")


if __name__ == '__main__':
    git_tag()
