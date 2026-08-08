# 练习购物车系统

# 商品包含价格，数量，商品名
class Product:
    def __init__(self,name,price,num):
        self.name=name
        self.price=price
        self.num=num

    def __str__(self):
        return (f"商品名称：{self.name} 商品价格：{self.price} 商品数量：{self.num}")

    def update_price(self,price=None,num=None):
        if price is not None:
            self.price=price
        if num is not None:
            self.num=num

# 购物车系统
class ShopManagement:
    system_version = 1.0
    system_name = "购物车系统"

    def __init__(self):
        self.product_list = []

    # 添加商品信息
    def add_product(self):
        name = input("请输入商品名称")

        for p in self.product_list :
            if p.name == name:
                print("已存在该商品请重新输入")
                return

        price = int(input("请输入商品价格"))
        num = int(input("请输入商品数量"))

        if 0 <= price and 0 <= num:
            shop = Product(name,price,num)
            self.product_list.append(shop)
            print("成功添加商品信息")
        else:
            print("商品信息有错，请重新添加 ")

    # 修改商品信息
    def update_product(self):
        name = input("请输入商品名称")
        for p in self.product_list :
            if p.name == name:
                print(f"当前商品信息是：{p}")

                price = int(input("请输入商品价格"))
                num = int(input("请输入商品数量"))
                if 0 <= price and 0 <= num:
                    p.update_price(price,num)
                    print(f"修改后商品信息是：{p}")
                    return
                else:
                    print("信息修改出错，请重试")
                    return

    # 根据名称删除对应商品
    def remove_product(self):
        name = input("请输入商品名称")
        for p in self.product_list :
            if p.name == name:
                self.product_list.remove(p)
                print("删除对应商品信息")
                return
            else:
                print("未找到对应商品")
                return

    # 查询商品
    def show_product(self):
        for p in self.product_list :
            print(p)


    def shop_run(self):
        print(f"欢迎使用教务系统{ShopManagement.system_version}")

        while True:
            print()
            print("---------------------------------------------------------------------------------")
            print("1.添加商品信息 2.修改商品信息 3.删除商品信息 4.展示所有商品信息 5.退出系统")
            print("---------------------------------------------------------------------------------")
            print()

            choice = input("\n 请输入序号1-5:")
            match choice:
                case "1":
                    self.add_product()
                case "2":
                    self.update_product()
                case "3":
                    self.remove_product()
                case "4":
                    self.show_product()
                case "5":
                    print("感谢使用此系统，再见")
                    break
                case _:
                    print("输入错误，请选择1-5之间的数")


if __name__ == '__main__':
    shop = ShopManagement()
    shop.shop_run()