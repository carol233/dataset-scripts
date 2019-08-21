# coding:utf-8
# python2
import hashlib
import json
import re
import os
import subprocess
import sqlite3
import pickle
import threading
import shutil
import threadpool

DREBIN_PATH = "../../../mnt/storage/yanjie/drebin"
DREBIN_GOOD_PATH = "../../../mnt/storage/yanjie/drebin_goodware"
GOODAPI_path = "../../../mnt/storage/yanjie/drebin_good_api"
MALAPI_path = "../../../mnt/storage/yanjie/drebin_mal_api"

p = re.compile(r'Landroid/.*?\(|Ljava/.*?\(')
find_file = re.compile(r'.smali$')
apidict = {}  # bianhao
tmp = "tmp"
debug = 1


def getApkList(rootDir):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if '.apk' in filename:
                file = os.path.join(parent, filename)
                filePath.append(file)

    return filePath


def getFileList(rootDir):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            file = os.path.join(parent, filename)
            filePath.append(file)

    return filePath


def get_number(string):
    if string not in apidict:
        apidict[string] = len(apidict)
    return str(apidict[string])


class Analysis:
    def __init__(self, apk_dir, save_dir):
        self.apk_dir = apk_dir
        self.save_dir = save_dir
        self.max_jobs = 20
        self.lock = threading.Lock()
        self.total_insert = 0

    def allover(self, apk_path):
        apkname = os.path.split(apk_path)[-1]
        if '.apk' in apkname:
            apkname = apkname[:-4]

        cmd = "../.local/bin/apktool d " + apk_path + " -o " + os.path.join(tmp, apkname + ".out") + " -p frametemp/"
        output = subprocess.check_output(cmd, shell=True)

        path = tmp + '/' + apkname + '.out' + '/smali'

        if not os.path.exists(path):
            shutil.rmtree(os.path.join(tmp, apkname + '.out'))
            return
        try:

            # print path
            all_thing = getFileList(path)
            this_call_num = 0
            this_dict = {}
            for thing in all_thing:
                try:
                    if not find_file.search(thing):
                        continue
                    f = open(thing, 'r')
                    for u in f:
                        match = p.findall(u)
                        for syscall in match:
                            this_call_num += 1
                            call_num = get_number(syscall)
                            if call_num in this_dict:
                                this_dict[call_num] += 1
                            else:
                                this_dict[call_num] = 1
                    f.close()
                except:
                    print('Can\'t open   ' + thing)

            logs = ['Landroid/util/Log;->v(', 'Landroid/util/Log;->e(', 'Landroid/util/Log;->w(',
                    'Landroid/util/Log;->i(',
                    'Landroid/util/Log;->d(']
            for log in logs:
                if get_number(log) in this_dict:
                    del this_dict[get_number(log)]
            if len(this_dict) == 0:
                shutil.rmtree(os.path.join(tmp, apkname + '.out'))
                return
            api_dict_str = str(json.dumps(this_dict))
            api_dict_md5 = hashlib.md5(api_dict_str).hexdigest()

            # save
            api_fname = os.path.join(self.save_dir, apkname + ".apidict")
            with open(api_fname, "w") as api_file:
                api_file.write(api_dict_md5)
            api_file.close()

            shutil.rmtree(os.path.join(tmp, apkname + '.out'))


        except Exception as e:
            print(e, apk_path)
            return None

    def start(self):
        apks = getApkList(self.apk_dir)
        print("total files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.allover, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()


if __name__ == '__main__':
    if not os.path.exists(tmp):
        os.mkdir(tmp)
    if not os.path.exists(GOODAPI_path):
        os.mkdir(GOODAPI_path)
    if not os.path.exists(MALAPI_path):
        os.mkdir(MALAPI_path)

    if os.path.exists("apidict_file.pkl"):
        pkl_file = open('apidict_file.pkl', 'rb')
        apidict = pickle.load(pkl_file)
        pkl_file.close()

    analysis = Analysis(DREBIN_PATH, MALAPI_path)
    analysis.start()

    analysis2 = Analysis(DREBIN_GOOD_PATH, GOODAPI_path)
    analysis.start()

    pkl_file = open("apidict_file.pkl", 'wb')
    pickle.dump(apidict, pkl_file)
    pkl_file.close()
