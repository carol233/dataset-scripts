# coding:utf-8

import os

GOODWARE_Feature = "../DREBIN_Goodfeature"
KEY = "fa08a4ad8d8c9d3c56236d27bd9b99bb83c66c3fd65642d496ea2cbd13d4e8a4"


def getApkList(rootDir):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        # 三个参数：分别返回 1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for filename in filenames:  # 输出文件信息
            if ".data" in filename:
                filename = filename[:-5]
            filePath.append(filename)

    return filePath


def process_one(apk):
    apk_path = apk + ".apk"
    try:
        cmd = "curl -O --remote-header-name -G -d apikey=" + KEY + " -d sha256=" + \
              apk + " --output " + apk_path + " https://androzoo.uni.lu/api/download"
        os.system(cmd)
    except Exception as e:
        print(e, apk)
        return None


if __name__ == '__main__':
    apks = getApkList(GOODWARE_Feature)
    for apk in apks:
        process_one(apk)
