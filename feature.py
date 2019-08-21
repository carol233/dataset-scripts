# coding:utf-8

import sqlite3
import os
import hashlib
import subprocess
import re
import threadpool
import threading

DREBIN_FEATURE = "D:/pythonTest/feature_vectors/feature_vectors"
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
            file = os.path.join(parent, filename)
            filePath.append(file)

    return filePath

class Analysis:
    def __init__(self, database_db):
        self.db_name = database_db
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_insert = 0

    def add_database(self,path):
        self.path = path

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
        c.execute("""CREATE TABLE IF NOT EXISTS DREBIN_FEATURE
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                      APK_MD5        TEXT    NOT NULL,
                      FEATURE        TEXT,
                      FEATURE_MD5    TEXT
                      );""")
        print("Table created successfully")
        conn.commit()
        self.conn = conn
        self.insert_count = 0
        self.sql_data = []

    def process_one(self, args):
        apk = args
        try:
            # APK MD5
            apk_item = open(apk, 'rb')
            feature = apk_item.read()
            feature_md5 = hashlib.md5(feature).hexdigest()
            apk_item.close()

            apk_md5 = os.path.split(apk)[-1]

            res = {
                "apk_md5": apk_md5,
                "feature": feature,
                "feature_md5": feature_md5
            }
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
            row = (res['apk_md5'], res['feature'], res['feature_md5'])
            self.sql_data.append(row)
            sql = "INSERT INTO DREBIN_FEATURE(APK_MD5, FEATURE, FEATURE_MD5) VALUES(?,?,?)"
            cursor = self.conn.cursor()
            cursor.executemany(sql, self.sql_data)
            self.conn.commit()
            self.sql_data = []
            self.insert_count = 0
        else:
            self.insert_count += 1
            row = (res['apk_md5'], res['feature'], res['feature_md5'])
            self.sql_data.append(row)

        self.lock.release()

    def process(self, dataset_path):
        apks = getApkList(dataset_path)
        print("total files ", len(apks))
        args = [(apk) for apk in apks]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args, self.save_result)
        [pool.putRequest(req) for req in requests]
        pool.wait()


    def start(self):
        self.connect_database()
        self.process(self.path)

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    analysis = Analysis('dataset.db')
    analysis.add_database(DREBIN_FEATURE)

    analysis.start()
