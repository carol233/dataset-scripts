# coding:utf-8

import os
import zipfile
import hashlib
import subprocess
import re
import threadpool
from tempfile import NamedTemporaryFile
import threading


# Global configuration
APIDICT_PATH = "../../../mnt/storage/yanjie/drebin_mal_opseq"
MOV_PATH = "../../../mnt/storage/yanjie/DREBIN_Malfeature"
PICKED_PATH = "../../../mnt/storage/yanjie/drebin_opcode/malfeature_picked"
tmp_file = "tmpfile.tmp"
debug = 1


def getApkList(rootDir, pick_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pick_str in filename: # exists .txt
                file = os.path.join(parent, filename)
                filePath.append(file)

    return filePath

class Analysis:
    def __init__(self, path, feature_path):
        self.api_dir = path
        self.feature_dir = feature_path
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_pick = 0
        self.opseq_md5 = {}


    def process_one(self, args):
        apk = args
        apk_sha256 = os.path.split(apk)[-1][:-6]
        try:

            f = open(apk, "rb")
            opseq_md5 = hashlib.sha256(f.read()).hexdigest()
            f.close()

            self.lock.acquire()
            if not opseq_md5 in self.opseq_md5:
                # cp
                mov_feature = os.path.join(self.feature_dir, apk_sha256 + ".data")
                os.system("cp " + mov_feature + " " + os.path.join(PICKED_PATH, apk_sha256 + ".data"))
                self.opseq_md5[opseq_md5] = 1
                self.total_pick += 1
            self.lock.release()

        except Exception as e:
            print(e, apk)
            return None


    def process(self, dir):
        apks = getApkList(dir, ".opseq")
        print("total files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    def start(self):
        self.process(self.api_dir)



if __name__ == '__main__':
    if not os.path.exists(PICKED_PATH):
        os.mkdir(PICKED_PATH)
    analysis = Analysis(APIDICT_PATH, MOV_PATH)
    analysis.start()
    print(analysis.total_pick)