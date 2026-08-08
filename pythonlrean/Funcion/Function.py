# # 函数定义
# def out_link():
#     print("-------------------")
#
# # 函数调用
#
# out_link()
from operator import truediv
from tkinter.constants import LEFT


# 三角形的面积
# def san(high,width):
#     return  (high * width) / 2
#
# print(san(10,5))
#
# # 输入一段字符串判断其中的元音字母
# def yuan(s):
#     num = 0
#     for w in s:
#         if w in 'aeiouAEIOU':
#             num +=1
#     return num
#
# print(yuan("Hello Wrold"))
#
# # 传入成绩列表计算最高，最低，平均
# def num_list(socre_list):
#     max_s = max(socre_list)
#     min_s = min(socre_list)
#     avg_s = round(sum(socre_list)/len(socre_list),1) #round内置函数可以选择保留小数
#     return max_s, min_s, avg_s
#
# print(num_list([98,89,55,96,52,22,10,35,150,26,20,10]))

# def select_num(numder):
#     if numder >= 90:
#         return print("A")
#     elif numder >= 75:
#         return print("B")
#     elif numder >= 60:
#         return print("C")
#     else:
#         return print("D")
#
# select_num(61)

def select_word(s:list) -> bool:
    clean = [c.lower() for c in s]
    left,right = 0,len(clean)-1
    while left < right:
        if clean[left] != clean[right]:
            return False
        else:
            left += 1
            right -= 1
            return True

print(select_word("asdfdsa"))

def sum_time(time):
    h = time // 3600
    nim = time %3600
    m = nim % 60
    s = nim // 60
    return print(f"{h}小时，{m}分钟，{s}秒")

sum_time(3661)