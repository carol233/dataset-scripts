# coding:utf-8
import os
import csv
import shutil

DREBIN_FEATURE = "D:/pythonTest/feature_vectors/feature_vectors"
MALWARE_CSV = "D:/pythonTest/sha256_family.csv"
DREBIN_Goodfeature = "D:/pythonTest/DREBIN_Goodfeature"
DREBIN_Malfeature = "D:/pythonTest/DREBIN_Malfeature"
malwares = {}


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


def movefile(filename, dir):
    shutil.copyfile(os.path.join(DREBIN_FEATURE, filename), os.path.join(dir, filename + ".data"))


def cut():
    if not os.path.exists(DREBIN_Goodfeature):
        os.mkdir(DREBIN_Goodfeature)
    if not os.path.exists(DREBIN_Malfeature):
        os.mkdir(DREBIN_Malfeature)
    allfiles = getFileList(DREBIN_FEATURE)
    for file in allfiles:
        filename = os.path.split(file)[-1]
        if filename in malwares:
            movefile(filename, DREBIN_Malfeature)
        else:
            movefile(filename, DREBIN_Goodfeature)



if __name__ == '__main__':
    with open(MALWARE_CSV) as csvfile:
        csv_reader = csv.reader(csvfile)
        malware_header = next(csv_reader)
        for row in csv_reader:
            malwares[row[0]] = row[1]
    cut()

