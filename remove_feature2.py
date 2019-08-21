# coding:utf-8
import hashlib
import os
import threading
import threadpool

PATH = "../../mnt/storage/yanjie/DREBIN_Malfeature"
PICKED_PATH = "../../mnt/storage/yanjie/DREBIN_Malfeature_picked"


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

class Analysis:
    def __init__(self, path):
        self.dir_path = path
        self.max_jobs = 15
        self.lock = threading.Lock()
        self.total_insert = 0
        self.feature_hash = {}


    def process_one(self, args):
        file = args
        try:
            # File MD5
            file_item = open(file, 'rb')
            feature = file_item.read()
            feature_md5 = hashlib.md5(feature).hexdigest()
            file_item.close()

            filename = os.path.split(file)[-1]

            self.lock.acquire()
            if feature_md5 not in self.feature_hash:
                # cp
                os.system("cp " + file + " " + os.path.join(PICKED_PATH, filename))
                self.feature_hash[feature_md5] = 1
            self.lock.release()

        except Exception as e:
            print(e, file)
            return None


    def process(self, dataset_path):
        files = getFileList(dataset_path)
        print("total files ", len(files))
        args = [(file) for file in files]
        pool = threadpool.ThreadPool(self.max_jobs)
        requests = threadpool.makeRequests(self.process_one, args)
        [pool.putRequest(req) for req in requests]
        pool.wait()


    def start(self):
        self.process(self.dir_path)


if __name__ == '__main__':
    if not os.path.exists(PICKED_PATH):
        os .mkdir(PICKED_PATH)
    analysis = Analysis(PATH)
    analysis.start()

