# import random

import random as rd
# 局部变量无法在函数外使用可以使用 global关键字将局部变量可以全局使用

# 混合传参时需要注意，需要使用位置传参的参数在前，关键字参数在后

# 不定长参数-位置传参 *args 将传入的参数存储在元组中
# 不定长参数-关键字传参 **参数满足键值对方式的传参

# def calc_data(*args):
#     max_data = max(args)
#     min_data =  min(args)
#     avg_data = sum(args) / len(args)
#     return max_data, min_data, avg_data
#
# print(calc_data(520,256,581,856,333,445))

# def calc_data(*args,**kwargs):
#     max_data = max(args)
#     min_data =  min(args)
#     avg_data = sum(args) / len(args)
#     # print(kwargs)
#     if kwargs.get('round') is not None:
#         avg_data = round(avg_data, kwargs.get('round'))
#
#     if kwargs.get('print'):
#         print("Max data: ", max_data)
#         print("Min data: ", min_data)
#
#     return max_data, min_data, avg_data
#
# print(calc_data(520,256,581,856,333,445,round=3,print=True))



# 匿名函数lambda

# data = lambda : print('hello world')
# data()


# 实现阶乘
"""
def jc(n):
     if n == 1:
         return 1
     else:
         return n * jc(n-1)

print(jc(10))
"""

# def clac_order_cost(*args,coupon,score,express):
#     total_pric = [goods[1]*goods[2] for goods in args ]
#     total_pric = sum(total_pric)
#
#     if total_pric >= 5000 and coupon <= total_pric:
#         total_pric -= coupon
#
#     if total_pric >= 5000 and score // 100 <= coupon:
#         total_pric -= score // 100
#
#     total_pric += express
#
#     return total_pric
#
#
# total = clac_order_cost(("鼠标",188,20),("键盘",359,30),coupon = 10,score= 4000,express= 9.9)
#
# print(total)

for i in range(37):
    print(rd.randint(1,100))
