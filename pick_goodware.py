# coding:utf-8

import sqlite3
import os
import zipfile
import hashlib
import subprocess
import re
import threadpool
from tempfile import NamedTemporaryFile
import threading

#apk 大写, data 小写

# Global configuration
GOODWARE_PATH = "../../../mnt/storage/yanjie/drebin_goodware"
MOV_PATH = "../../../mnt/storage/yanjie/DREBIN_Goodfeature"
PICKED_PATH = "../../../mnt/storage/yanjie/drebin_dex/goodfeature_picked"
tmp_file = "tmpfile.tmp"
debug = 1


def getApkList(rootDir):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        # 三个参数：分别返回 1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for filename in filenames:  # 输出文件信息
            if not ".apk" in filename:
                continue
            file = os.path.join(parent, filename)
            filePath.append(file)

    return filePath

class Analysis:
    def __init__(self, path, mov_path):
        self.dir = path
        self.mov_dir = mov_path
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_pick = 0
        self.developer = {}
        self.dex_md5 = {}


    def process_one(self, args):
        apk = args
        apk_md5 = os.path.split(apk)[-1][:-4].lower()
        try:
            mov_data = os.path.join(self.mov_dir, apk_md5 + ".data")
            os.system("cp " + mov_data + " " + os.path.join(PICKED_PATH, apk_md5 + ".data"))

        except Exception as e:
            print(e, apk)
            return None


    def process(self, dir):
        apks = getApkList(dir)
        print("total files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    def start(self):
        self.process(self.dir)


if __name__ == '__main__':
    if not os.path.exists(PICKED_PATH):
        os.mkdir(PICKED_PATH)
    analysis = Analysis(GOODWARE_PATH, MOV_PATH)
    analysis.start()
