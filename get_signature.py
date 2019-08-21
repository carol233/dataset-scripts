# coding:utf-8

import os
import subprocess
import threadpool
import threading


# Global configuration
DREBIN_PATH = "../../../mnt/storage/yanjie/drebin"
SIG_PATH = "../../../mnt/storage/yanjie/drebin_mal_sig"
debug = 1


def getApkList(rootDir, filtername):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if not filtername in filename:
                continue
            file = os.path.join(parent, filename)
            filePath.append(file)

    return filePath


class Analysis:
    def __init__(self, path, sig_path):
        self.dir = path
        self.sig_path = sig_path
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_pick = 0
        self.developer = {}


    def process_one(self, args):
        apk = args
        apk_sha256 = os.path.split(apk)[-1][:-4]
        try:

            cmd = "./bin/print-apk-signature.sh " + apk + " MD5"
            output = subprocess.check_output(cmd, shell=True)

            result = str(output).strip()
            if result:
                savepath = os.path.join(self.sig_path, apk_sha256 + ".sig")
                fw = open(savepath, 'w')
                fw.write(result)
                fw.close()

        except Exception as e:
            print(e, apk)
            return None


    def process(self, dir):
        apks = getApkList(dir, '.apk')
        print("total files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()

    def start(self):
        self.process(self.dir)



if __name__ == '__main__':
    if not os.path.exists(SIG_PATH):
        os.mkdir(SIG_PATH)
    analysis = Analysis(DREBIN_PATH, SIG_PATH)
    analysis.start()


