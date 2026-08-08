class Car:
    def __init__(self, c_color,c_brand,c_name,c_price):
        self.color = c_color
        self.brand = c_brand
        self.name = c_name
        self.price = c_price
        print("Car类的属性已经初始化")

    def running(self):
        print(f"{self.brand} {self.name} 正在高速行驶中.....")

    def total_price(self,discount,rate):
        total_price = self.price * discount + rate * self.price
        return total_price
# 创建对象
c1 = Car("red","BMW","X5",500000)

# 动态添加属性（不推荐）
# c1.color = "red"
# c1.brand = "BMW"
# c1.name = "X5"
# c1.price = 50

c1.running()
total = c1.total_price(0.2,0.3)
print("提车的总费用是：",total)