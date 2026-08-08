import json
from plistlib import dump

d = {
    "name": "张三",
    "age": 30,
    "height": 1.5,
    "weight": 2.5,
    "eye_color": "blue",
}
print(str(d))
s = json.dumps(d,ensure_ascii=False)
print(s)