"""
计算两个向量的余弦相似度（衡量方向相似性，剔除长度影响）

参数：
    vec_a (np.array): 向量A
    vec_b (np.array): 向量B
返回：
    float: 余弦相似度结果（范围[-1,1]，越接近1方向越一致）
公式：
    cos_sim = (vec_a · vec_b) / (||vec_a|| × ||vec_b||)
    拆解：
    1. 点积：vec_a · vec_b = vec_a[0]×vec_b[0] + vec_a[1]×vec_b[1] + ... + vec_a[n]×vec_b[n]
    2. 模长：||vec_a|| = √(vec_a[0]² + vec_a[1]² + ... + vec_a[n]²)
    3. 模长：||vec_b|| = √(vec_b[0]² + vec_b[1]² + ... + vec_b[n]²)

A: [0.5, 0.5]
B: [0.7, 0.7]
C: [0.7, 0.5]
D: [-0.6, -0.5]
"""
import numpy as np

def get_dot(vec_a, vec_b):
    """计算两个向量的点积，2个向量维度数字乘积之和"""
    if len(vec_a) != len(vec_b):
        return -1
    dot_sum = 0
    for a,b in zip(vec_a, vec_b):
        dot_sum += a * b

        return dot_sum
def get_norm(vec):
    """计算向量的模长，向量维度数字平方和的平方根"""
    sum_square = 0
    for v in vec:
        sum_square += v*v

    # numpy 计算平方根
        return np.sqrt(sum_square)

def cosine_similarity(vec_a, vec_b):
    """计算两个向量的余弦相似度，衡量方向相似性，剔除长度影响"""
    result = get_dot(vec_a, vec_b) / (get_norm(vec_a)*get_norm(vec_b))
    return result

if __name__ == '__main__':
    vec_a = np.array([0.5, 0.5])
    vec_b = np.array([0.7, 0.7])

    print("A和B的余弦相似度为：", cosine_similarity(vec_a, vec_b))
