# 学生类存储学生信息（成绩，姓名）
class Student:
    def __init__(self,name,chinese,math,english):
        self.name=name
        self.chinese=chinese
        self.math=math
        self.english=english

    def __str__(self):
        return (f"姓名:{self.name} | 语文：{self.chinese} | 数学：{self.math} | "
                f"英语：{self.english} | 总分：{self.chinese+self.math+self.english}")

    def update_score(self,chinese=None,math=None,english=None):
        if chinese is not None:
            self.chinese = chinese
        if math is not None:
            self.math = math
        if english is not None:
            self.english = english



class EduManagement:
    system_version=1.0
    system_name="教务管理系统"

    def __init__(self):
        self.student_list = []

    # 添加学生成绩
    def add_student(self):
        name = input("请输入学生姓名：")

        for s in self.student_list:
            if s.name == name:
                print("该学生已经存在，添加失败")
                return

        chinese = int(input("请输入语文成绩："))
        math = int(input("请输入数学成绩："))
        english = int(input("请输入英语成绩："))

        if 0 <= chinese <= 100 and 0 <= math <= 100 and 0 <= english <= 100:
            stu = Student(name,chinese,math,english)
            self.student_list.append(stu)
            print("学生信息添加成功")
        else:
            print("信息错误请重新添加")


    # 修改学生成绩
    def update_student(self):
        name = input("输入学生姓名")

        for s in self.student_list:
            if s.name == name:
                print(f"当前成绩是：{s}")

                chinese = int(input("请输入修改语文成绩："))
                math = int(input("请输入修改数学成绩："))
                english = int(input("请输入修改英语成绩："))


                if 0 <= chinese <= 100 and 0 <= math <= 100 and 0 <= english <= 100:
                    s.update_score(chinese,math,english)
                    print(f"修改之后的成绩是{s}")
                    return

                else:
                    print("信息错误请重新修改")
                    return

        print("未找到该学生，修改失败")


    # 删除学生成绩
    def remove_student(self):
        name = input("请输入学生姓名")

        for s in self.student_list:
            if s.name == name:
                self.student_list.remove(s)
                print("删除对应学生信息")
                return

            else:
                print("未找到该学生，无法删除")
                return

    # 查询指定学生成绩
    def query_student(self):
        name = input("请输入要查询学生姓名")

        for s in self.student_list:
            if s.name == name:
                print(f"该学生信息是{s}")
                return
            else:
                print("未找到该学生，查询失败")
                return

    # 展示所有学生信息
    def list_student(self):
        for s in self.student_list:
            print(s)

    # 运行系统界面
    def run (self):
        print(f"欢迎使用教务系统{EduManagement.system_version}")

        while True:
            print()
            print("---------------------------------------------------------------------------------")
            print("1.添加学生成绩 2.修改学生 3.删除学生 4.查询指定学生 5.查询所有学生 6.退出系统")
            print("---------------------------------------------------------------------------------")
            print()


            choice = input("\n请输入要执行操作的序号，1-6:")

            try:
                match choice:
                    case "1":
                        self.add_student()
                    case "2":
                        self.update_student()
                    case "3":
                        self.remove_student()
                    case "4":
                        self.query_student()
                    case "5":
                        self.list_student()
                    case "6":
                        print("感谢使用，系统已退出")
                        break
                    case _:
                        print("输入错误，请选择1-6之间的数")
            except ValueError:
                print("输入的数据有问题，请重新输入")
            except Exception:
                print("程序与逆行出错了，请重新选择")


if __name__ == '__main__':
    edu = EduManagement()
    edu.run()