# coding:utf-8
import csv
import os
import random
import zipfile
import hashlib
import subprocess
import re
import threadpool
from tempfile import NamedTemporaryFile
import threading


# Global configuration
FAMILYFILE_PATH = "../drebin/sha256_family.csv"
MOV_PATH = "../../../mnt/storage/yanjie/DREBIN_Malfeature"
PICKED_PATH = "../../../mnt/storage/yanjie/familydatasets/mal1kno1"
tmp_file = "tmpfile.tmp"
debug = 1

family_dict = {}
family_count = {}
total_pick = 0

def getApkList(rootDir, pick_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pick_str in filename:  # exists .txt
                file = os.path.join(parent, filename)
                filePath.append(file)

    return filePath


def count():
    with open(FAMILYFILE_PATH, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)  # 浣跨敤csv.reader璇诲彇csvfile涓殑鏂囦欢
        birth_header = next(csv_reader)  # 璇诲彇绗竴琛屾瘡涓€鍒楃殑鏍囬
        for row in csv_reader:
            sha256 = row[0]
            family = row[1]
            family_dict[sha256] = family


def process_one(args):
    global total_pick
    apk = args
    apk_sha256 = apk
    family = family_dict[apk_sha256]
    try:
        if family in family_count:
            if family_count[family] >= 22:
                return
            # cp
            mov_feature = os.path.join(MOV_PATH, apk_sha256 + ".data")
            os.system("cp " + mov_feature + " " + os.path.join(PICKED_PATH, apk_sha256 + ".data"))
            family_count[family] += 1
            total_pick += 1
        else:
            mov_feature = os.path.join(MOV_PATH, apk_sha256 + ".data")
            os.system("cp " + mov_feature + " " + os.path.join(PICKED_PATH, apk_sha256 + ".data"))
            family_count[family] = 1
            total_pick += 1
    except Exception as e:
        print(e, apk)
        return None


def main():
    count()
    keys = family_dict.keys()
    random.shuffle(keys)
    for apk in keys:
        process_one(apk)



if __name__ == '__main__':
    if not os.path.exists(PICKED_PATH):
        os.mkdir(PICKED_PATH)
    main()
    print(total_pick)