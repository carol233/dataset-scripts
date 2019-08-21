# coding:utf-8
import csv

path = "sha256_family.csv"

def main(cav_path):
    family_dict = {}
    with open(cav_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        birth_header = next(csv_reader)  # 读取第一行每一列的标题
        for row in csv_reader:
            family = row[1]
            sha256 = row[0]
            if family in family_dict:
                family_dict[family] += 1
            else:
                family_dict[family] = 1

    return family_dict

if __name__ == '__main__':
    dict1 = main(path)
    count = 0
    count2 = 0
    for item in dict1:
        if dict1[item] > 200:
            count += 1
            print(item, dict1[item])
        else:
            count2 += dict1[item]
    print(count)
    print(count2)