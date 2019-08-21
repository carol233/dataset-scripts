# coding:utf-8

import sqlite3
import os
import zipfile
import hashlib
import subprocess
import re
import threadpool
import multiprocessing
from tempfile import NamedTemporaryFile
import threading


# Global configuration
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
            file = os.path.join(parent, filename)  # 输出文件路径信息
            filePath.append(file)

    return filePath

class Analysis:
    def __init__(self, database_db):
        self.db_name = database_db
        self.databases = {}
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_insert = 0

    def add_database(self, name, path):
        self.databases[name] = path

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
        c.execute("""CREATE TABLE IF NOT EXISTS DATA
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                      DATASET        TEXT    NOT NULL,
                      PATH           TEXT    NOT NULL,
                      APK_MD5        TEXT    NOT NULL,
                      DEX_MD5        TEXT,
                      DEVELOPER      TEXT,
                      API            TEXT    
                      );""")
        print("Table created successfully")
        conn.commit()
        self.conn = conn
        self.insert_count = 0
        self.sql_data = []

    def process_one(self, args):
        dataset, dataset_path, apk = args
        try:
            # APK MD5
            apk_item = open(apk, 'rb')
            apk_md5 = hashlib.md5(apk_item.read()).hexdigest()
            apk_item.close()

            # DEX MD5
            dex_md5 = "none"
            z = zipfile.ZipFile(apk)

            if "classes.dex" in z.namelist():
                dex_item = z.open("classes.dex", 'r')
                dex_md5 = hashlib.md5(dex_item.read()).hexdigest()

            # SIG
            sign_md5 = "none"
            rsa_files = filter(lambda x: x.endswith("RSA"), z.namelist())
            for rsa_file in rsa_files:
                tmpfile = NamedTemporaryFile(delete=False)
                tmpfile.write(z.open(rsa_file, 'r').read())
                tmpfile.close()
                cmd = "keytool -printcert -file " + tmpfile.name
                output = subprocess.check_output(cmd, shell=True)

                result = re.findall(r'MD5:\s+([0-9A-Z:]+)', str(output))
                if result:
                    sign_md5 = result[0].strip()
            z.close()

            apk_path = os.path.relpath(apk, dataset_path)
            API = "none"

            res = {
                "dataset": dataset,
                "path": apk_path,
                "apk_md5": apk_md5,
                "dex_md5": dex_md5,
                "developer": sign_md5,
                "api": API
            }
            # print(res)
            return res
        except Exception as e:
            print(e, apk)
            return None

    def save_result(self, request, res):
        # if catch exception
        if not res:
            return

        self.lock.acquire()
        self.total_insert += 1
        if self.total_insert % 10 == 0:
            print(self.total_insert)

        if self.insert_count > 400:
            row = (res['dataset'], res['path'], res['apk_md5'],
                   res['dex_md5'], res['developer'], res['api'])
            self.sql_data.append(row)
            sql = "INSERT INTO DATA(DATASET, PATH, APK_MD5, DEX_MD5, DEVELOPER, API) VALUES(?,?,?,?,?,?)"
            cursor = self.conn.cursor()
            cursor.executemany(sql, self.sql_data)
            self.conn.commit()
            self.sql_data = []
            self.insert_count = 0
        else:
            self.insert_count += 1
            row = (res['dataset'], res['path'], res['apk_md5'],
                   res['dex_md5'], res['developer'], res['api'])
            self.sql_data.append(row)

        self.lock.release()

    def process(self, dataset, dataset_path):
        apks = getApkList(dataset_path)
        print("total files ", len(apks))
        args = [([dataset, dataset_path, apk]) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args, self.save_result)
        [pool.putRequest(req) for req in requests]
        pool.wait()


    def start(self):
        self.connect_database()
        for name in self.databases:
            self.process(name, self.databases[name])

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    analysis = Analysis('dataset.db')
    analysis.add_database('drebin', "G:\Malware\drebin")
    analysis.add_database('genome', "G:\Malware\genomeapps\malware_genome\samples")
    analysis.add_database('virusshare', "G:\Malware\VirusShare_Android_20130506")
    analysis.add_database('rmvdroid', "G:\Malware\RmvDroid\RmvDroid")

    analysis.start()
