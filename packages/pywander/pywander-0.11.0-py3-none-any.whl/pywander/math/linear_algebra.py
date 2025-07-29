"""
linear algebra

本脚本只考虑基于numpy的ndarray的情况，对向量，矩阵等各个数学运算提供支持。

the prefix explanation

a : an array np.array([1, 2, 3])

v : 行向量和列向量和1d_array
    一般应用场景是不需要确立所谓数学意义上严格的行向量和列向量的，但在某些情景下，要求实现列向量和行向量的点积输出是一个矩阵，
    这个时候行向量和列向量和1d_array都需要严格进行区分，如下所示：

    1d array:  np.array([1, 2, 3])
    row_vector  np.array([[1,2,3]])
    col_vector  np.array([[2],[0],[0]])

m : the linear equation system left matrix

b : the linear equation right b array

am : [argumented matrix] combine m and b to a entire linear system matrix

"""

import numpy as np


def is_1d_array(arr):
    """
    1d array 这是最常见的数据结构形式
    1d array: np.array([1, 2, 3])
    """
    # 方法一：使用 ndim 属性判断
    # 方法二：使用 shape 属性判断
    return arr.ndim == 1 or len(arr.shape) == 1


def is_row_vector(arr):
    """
    是否是行向量
    """
    # 首先检查数组的维度是否为 2
    if arr.ndim == 2:
        # 再检查数组的形状是否为 (1, n) 的形式
        if arr.shape[0] == 1:
            return True
    return False

def is_column_vector(arr):
    """
    是否是列向量
    """
    # 首先检查数组是否为二维数组
    if arr.ndim == 2:
        # 然后检查数组的第二维（列）长度是否为 1
        return arr.shape[1] == 1
    return False

def to_row_vector(one_d_array):
    """
    转成行向量
    要求输入参数为1d array
    """
    if is_1d_array(one_d_array):
        row_vector = one_d_array.reshape(1, -1)
        return row_vector
    raise Exception('please input 1d array')


def to_column_vector(one_d_array):
    """
    转成列向量
    要求输入参数为1d array
    """
    if is_1d_array(one_d_array):
        return one_d_array.reshape(-1, 1)
    else:
        raise ValueError("please input 1d array.")


def column_vector_to_row_vector(col_v):
    """
    列向量转成行向量
    直接用transpose即可，本函数严格要求输入是列向量
    """
    if is_column_vector(col_v):
        return col_v.transpose()
    else:
        raise ValueError("please input the column vector.")

def row_vector_to_column_vector(row_v):
    """
    行向量转成列向量
    直接用transpose即可，本函数严格要求输入是行向量
    """
    if is_row_vector(row_v):
        return row_v.transpose()
    else:
        raise ValueError("please input the row vector.")


def dimension_of_linear_combination(*vec):
    vec_num = len(vec)

    matrix = np.column_stack(vec)
    # 计算矩阵的秩
    rank = np.linalg.matrix_rank(matrix)
    # 判断秩
    if rank == vec_num:
        print(f'这组向量的线性组合组成的向量空间维度为 {rank} ,等于向量数,这组向量是线性无关的.')

    if rank == 1:
        print(f'这组向量的线性组合是向量空间中的一条直线.')
    elif rank == 2:
        print(f'这组向量的线性组合是向量空间中的一个平面.')
    else:
        print(f'这组向量的线性组合是向量空间中的{rank}维空间 $\\mathbb{{R}}^{rank}$ .')


def can_form_plane(vec1, vec2):
    # 将两个向量按列拼接成矩阵
    matrix = np.column_stack((vec1, vec2))
    # 计算矩阵的秩
    rank = np.linalg.matrix_rank(matrix)
    # 判断秩是否为 2
    return bool(rank == 2)


def can_form_3d_space(vec1, vec2, vec3):
    # 将三个向量按列拼接成矩阵
    matrix = np.column_stack((vec1, vec2, vec3))
    # 计算矩阵的秩
    rank = np.linalg.matrix_rank(matrix)
    # 判断秩是否为 3
    return bool(rank == 3)



def l1norm(v):
    """
    返回向量的l1范数

    注意本函数只考虑向量或者一维数组的情况
    """
    return np.linalg.norm(v, 1)


def l2norm(v):
    """
    返回向量的l2范数

    注意本函数只考虑向量或者一维数组的情况
    """
    return np.linalg.norm(v, 2)


def vector_length(v):
    """
    向量的长度
    """
    return l2norm(v)


def cosine_similarity(v1, v2):
    """
    calc the cosine similarity between two vectors.
    Parameters
    ----------
    v1
    v2

    Returns
    -------

    """
    cosine = np.dot(v1, v2) / (vector_length(v1) * vector_length(v2))
    return cosine


def normalize_l1(vector):
    """
    对向量进行 L1 归一化

    注意本函数只考虑向量或者一维数组的情况
    """
    norm = l1norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def normalize_l2(vector):
    """
    对向量进行 L2 归一化

    注意本函数只考虑向量或者一维数组的情况
    """
    norm = l2norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def minmax_scale(arr, feature_range=(0.01, 0.99)):
    """
    将数组中的所有数字缩放到指定的范围 [min_val, max_val]

    `sklearn.preprocessing.minmax_scale` 太重了，是专门针对机器学习那一套流程而设计的

    本函数只关注于一些简单的原型设计，就是简单的一维数组进行minmax缩放
    """
    min_val = feature_range[0]
    max_val = feature_range[1]

    # 找到数组中的最小值和最大值
    arr_min = np.min(arr)
    arr_max = np.max(arr)
    # 进行线性缩放
    scaled_arr = min_val + (arr - arr_min) / (arr_max - arr_min) * (max_val - min_val)
    return scaled_arr


def cosine_similarity_after_normalization(vector1, vector2):
    """
    先对向量进行归一化，再计算余弦相似度

    和cosine_similarity必然输出一样的结果 也就是余弦相似度本质上就和向量长度无关
    """
    normalized_vector1 = normalize_l2(vector1)
    normalized_vector2 = normalize_l2(vector2)
    # 由于向量已归一化，模长都为 1，余弦相似度就是点积
    # 所以某些情况下向量已经归一化了 这个时候直接计算点积就得到余弦相似度了
    return np.dot(normalized_vector1, normalized_vector2)


def swap_rows(m, row_num_1, row_num_2):
    """
    Gaussian elimination basic operation 1
    swap two rows
    """
    m_new = m.copy()
    m_new[[row_num_1, row_num_2]] = m_new[[row_num_2, row_num_1]]
    return m_new


def multiply_row(m, row_num, row_num_multiple):
    """
    Gaussian elimination basic operation 2
    """
    m_new = m.copy()
    m_new[row_num] = m_new[row_num] * row_num_multiple
    return m_new


def add_rows(m, row_num_1, row_num_2, row_num_1_multiple):
    """
    Gaussian elimination basic operation 3
    """
    m_new = m.copy()
    m_new[row_num_2] = row_num_1_multiple * m_new[row_num_1] + m_new[row_num_2]
    return m_new


def solve(m, b):
    """
    solve the linear equation system
    """
    return np.linalg.solve(m, b)


def determinant(m):
    """
    calc the determinant
    """
    return np.linalg.det(m)


def combine_system(m, b):
    """
    combine m and b to system
    """
    return np.hstack((m, b.reshape(b.size, 1)))


def matrix_multiplication(m1, m2):
    """
    notice: ndim=1 array is a vector, can not apply here.
    """
    return np.matmul(m1, m2)
