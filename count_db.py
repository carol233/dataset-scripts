# coding:utf-8

import sqlite3

class Analysis:
    def __init__(self, database):
        self.database = database
        self.conn = sqlite3.connect(self.database)

    def select_query(self, db):
        cu = self.conn.cursor()

        sql = """select * from (select count(*) as num from data 
                      where dataset = '""" + db + """' and dex_md5 != 'none' group by dex_md5) where num > 1"""

        results = cu.execute(sql)
        tmplist = results.fetchall()
        count = 0
        for item in tmplist:
            num = item[0]
            count += num
        return count


if __name__ == '__main__':
    analysis = Analysis("dataset.db")

    result = analysis.select_query("drebin")
    print("drebin:", result)

    result = analysis.select_query("genome")
    print("genome:", result)

    result = analysis.select_query("virusshare")
    print("virusshare:", result)

    result = analysis.select_query("rmvdroid")
    print("rmvdroid:", result)


