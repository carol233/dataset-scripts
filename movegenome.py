# coding:utf-8
import os

PATH = "genome_malware"
NEW_PATH = "genome"

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


if __name__ == '__main__':
    apklist = getApkList(PATH, '.apk')
    for file in apklist:
        filename = os.path.split(file)[-1]
        os.system("cp " + file + " " + os.path.join(NEW_PATH, filename))