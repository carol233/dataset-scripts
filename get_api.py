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

PATH = "../../../mnt/storage/yanjie/drebin"
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
            if (not '.apk' in filename) and ('.' in filename) or 'drebin' in filename:
                continue
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
    def __init__(self, dbname, path):
        self.db_name = dbname
        self.dir = path
        self.max_jobs = 10
        self.lock = threading.Lock()
        self.total_insert = 0

    def connect_database(self):
        """
        :param database: filepath of database
        :return: sqlite connection
        """
        if debug and os.path.exists(self.db_name):
            os.remove(self.db_name)

        conn = sqlite3.connect(self.db_name)
        print("Opened database successfully")

        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS API
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                      APK_PATH       TEXT    NOT NULL,
                      APK_MD5        TEXT    NOT NULL,
                      TOTAL_NUM      INTEGER,
                      TOTAL_CALL     INTEGER,
                      API_DICT       TEXT,
                      API_DICT_MD5   TEXT
                      );""")
        print("Table created successfully")
        conn.commit()
        self.conn = conn
        self.insert_count = 0
        self.sql_data = []


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
            #apk md5
            apk_item = open(apk_path, 'rb')
            apk_md5 = hashlib.md5(apk_item.read()).hexdigest()
            apk_item.close()
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

            logs = ['Landroid/util/Log;->v(', 'Landroid/util/Log;->e(', 'Landroid/util/Log;->w(', 'Landroid/util/Log;->i(',
                    'Landroid/util/Log;->d(']
            for log in logs:
                if get_number(log) in this_dict:
                    del this_dict[get_number(log)]
            if len(this_dict) == 0:
                shutil.rmtree(os.path.join(tmp, apkname + '.out'))
                return
            api_dict_str = str(json.dumps(this_dict))
            api_dict_md5 = hashlib.md5(api_dict_str).hexdigest()
            package = {'apk_path': apk_path, 'apk_md5': apk_md5, 'total_num': len(this_dict),
                       'total_call': this_call_num, 'api_dict': api_dict_str, 'api_dict_md5': api_dict_md5}
            # print(package)
            shutil.rmtree(os.path.join(tmp, apkname + '.out'))
            return package

        except Exception as e:
            print(e, apk_path)
            return None


    def save_result(self, request, res):
        # if catch exception
        if not res:
            return

        self.lock.acquire()
        self.total_insert += 1
        if self.total_insert % 10 == 0:
            print(self.total_insert)

        if self.insert_count > 20:
            row = (res['apk_path'], res['apk_md5'], res['total_num'],
                   res['total_call'], res['api_dict'], res['api_dict_md5'])
            self.sql_data.append(row)
            sql = "INSERT INTO API(APK_PATH, APK_MD5, TOTAL_NUM, TOTAL_CALL, API_DICT, API_DICT_MD5) VALUES(?,?,?,?,?,?)"
            cursor = self.conn.cursor()
            cursor.executemany(sql, self.sql_data)
            self.conn.commit()
            self.sql_data = []
            self.insert_count = 0
        else:
            self.insert_count += 1
            row = (res['apk_path'], res['apk_md5'], res['total_num'],
                   res['total_call'], res['api_dict'], res['api_dict_md5'])
            self.sql_data.append(row)

        self.lock.release()


    def intodb(self):

        apks = getApkList(PATH)
        print("total files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.allover, args, self.save_result)
        [pool.putRequest(req) for req in requests]
        pool.wait()


if __name__ == '__main__':
    if not os.path.exists(tmp):
        os.mkdir(tmp)

    if os.path.exists("apidict.pkl"):
        pkl_file = open('apidict.pkl', 'rb')
        apidict = pickle.load(pkl_file)
        pkl_file.close()

    analysis = Analysis("api.db", PATH)
    analysis.connect_database()
    analysis.intodb()

    pkl_file = open("apidict.pkl", 'wb')
    pickle.dump(apidict, pkl_file)
    pkl_file.close()
