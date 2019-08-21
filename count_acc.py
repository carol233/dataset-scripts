# coding:utf-8

test1 = [0.92, 0.87, 0.90, 0.87, 0.89, 0.91, 0.90, 0.91, 0.91, 0.91]
test2 = [0.88, 0.90, 0.88, 0.88, 0.88, 0.88, 0.89, 0.88, 0.87, 0.89]
test3 = [0.91, 0.91, 0.89, 0.90, 0.93, 0.89, 0.93, 0.91, 0.88, 0.89]
test4 = [0.87, 0.87, 0.87, 0.88, 0.86, 0.89, 0.87, 0.89, 0.88, 0.89]

def count1(test_list):
    sum = 0
    for item in test_list:
        sum += item
    return sum/len(test_list)

if __name__ == "__main__":
    print(count1(test1))
    print(count1(test2))
    print(count1(test3))
    print(count1(test4))


