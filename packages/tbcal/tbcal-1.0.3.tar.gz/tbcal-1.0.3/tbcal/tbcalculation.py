import numpy as np
from cmath import exp, sqrt
from math import pi
import math



def high_symmetry_line(
        HSP: np.ndarray = np.array([[pi,pi], [pi,0], [0,0], [pi,pi]]), 
        step=0.1
    ):
    '''
    每隔 step 步长在HSP二维空间点之间插入一个点
    '''
    kx_array = np.array([HSP[0][0]])
    ky_array = np.array([HSP[0][1]])
    for i in range(HSP.shape[0]-1):
        x = HSP[i+1][0] - HSP[i][0]
        y = HSP[i+1][1] - HSP[i][1]
        k_len= sqrt(x*x + y*y)
        k_number = math.floor(k_len/step) + 1
        kx = np.linspace(HSP[i][0], HSP[i+1][0], k_number)
        kx_array = np.concatenate((kx_array, kx[1:]), axis=0)
        ky = np.linspace(HSP[i][1], HSP[i+1][1], k_number)
        ky_array = np.concatenate((ky_array, ky[1:]), axis=0)
    return kx_array, ky_array



def high_symmetry_line_3D(
        HSP: np.ndarray = np.array([[0,0,0], [pi,0,0], [pi,pi,0], [pi,pi,pi], [0,0,0]]), 
        step=0.1
    ):
    '''
    每隔 step 步长在HSP二维空间点之间插入一个点
    '''
    kx_array = np.array([HSP[0][0]])
    ky_array = np.array([HSP[0][1]])
    kz_array = np.array([HSP[0][2]])
    for i in range(HSP.shape[0]-1):
        x = HSP[i+1][0] - HSP[i][0]
        y = HSP[i+1][1] - HSP[i][1]
        z = HSP[i+1][2] - HSP[i][2]
        k_len= sqrt(x*x + y*y + z*z)
        k_number = math.floor(k_len/step) + 1
        kx = np.linspace(HSP[i][0], HSP[i+1][0], k_number)
        kx_array = np.concatenate((kx_array, kx[1:]), axis=0)
        ky = np.linspace(HSP[i][1], HSP[i+1][1], k_number)
        ky_array = np.concatenate((ky_array, ky[1:]), axis=0)
        kz = np.linspace(HSP[i][2], HSP[i+1][2], k_number)
        kz_array = np.concatenate((kz_array, kz[1:]), axis=0)
    return kx_array, ky_array, kz_array



def get_val_vec(func, data=None):
    '''
    当func为函数时，data传入列表，元素个数为func参数个数，
    每个元素为可迭代对象。
    func也可以是np.ndarray
    返回 val_array(1D), vec_array(2D,axis=1 is index)
    '''
    # 检查传入参数是否已经是矩阵
    if type(func) == np.ndarray:
        matrix = func
        para_num = 0
    else:
        # func 为tbmodel类的方法，因而参数个数要去掉self
        para_num:int = func.__code__.co_argcount -1
    if para_num == 0:
        try:
            matrix
        except:
            matrix = func()
        eigenvalue1, eigenvector1 = np.linalg.eig(matrix)
        arg = np.argsort(eigenvalue1.real)
        eigenvalue = eigenvalue1[arg]
        eigenvector = eigenvector1[:,arg]
        return  eigenvalue,eigenvector

    # solve matrix, results append to val_array, vec_array
    def calcu(matrix,val_array, vec_array):
        eigenvalue1, eigenvector1 = np.linalg.eig(matrix)
        arg = np.argsort(eigenvalue1.real)
        eigenvalue = eigenvalue1[arg]
        eigenvector = eigenvector1[:,arg]
        val_array = np.append(val_array, eigenvalue)
        vec_array = np.concatenate((vec_array, eigenvector), axis=1)
        return val_array, vec_array

    if para_num == 1:
        n = func(0).shape[0]
        val_array = np.empty(0)*0j
        vec_array = np.empty((n,0))*0j
        for item in data:
            matrix = func(item)
            val_array, vec_array = calcu(matrix, val_array, vec_array)
    if para_num == 2:
        n = func(0,0).shape[0]
        val_array = np.empty(0)*0j
        vec_array = np.empty((n,0))*0j
        for kx, ky in zip(data[0], data[1]):
            matrix = func(kx,ky)
            val_array, vec_array = calcu(matrix, val_array, vec_array)
    if para_num == 3:
        n = func(0,0,0).shape[0]   
        val_array = np.empty(0)*0j
        vec_array = np.empty((n,0))*0j 
        for kx, ky, kz in zip(data[0], data[1], data[2]):
            matrix = func(kx,ky,kz)
            val_array, vec_array = calcu(matrix, val_array, vec_array)
    return  val_array,vec_array



def ray_casting_method(x, y, polygon):
    '''
    射线法确定点(x,y)是否在多边形内
    '''
    n = len(polygon)
    count = 0
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i+1)%n]
        if y < min(p1[1], p2[1]):
            continue
        if y > max(p1[1], p2[1]):
            continue
        # 遍历每条边时，区间前闭后开[p1,p2),避免重复计算
        if y == p2[1]:
            continue
        # 注意保证p2[1]-p1[1]不为0
        xinters = (y-p1[1])*(p2[0]-p1[0])/(p2[1]-p1[1])+p1[0]
        if x < xinters:
            count += 1
        # 如果在边上直接返回True
        if x == xinters:
            count += 1
            return True
    return bool(count % 2)



def cut_OBC(matrix, x_pos, y_pos, polygon):
    '''
    matrix为矩阵，x_pos, y_pos为矩阵对应的坐标，
    polygon为多边形顶点坐标。
    返回多边形内的矩阵和对应的坐标
    射线法确定多边形内的点
    '''
    
    x_pos_new = np.array(x_pos).copy()
    y_pos_new = np.array(y_pos).copy()
    matrix_new = matrix.copy()

    for i in np.arange(len(x_pos)-1, -1, -1):
        if not ray_casting_method(x_pos[i], y_pos[i], polygon):
            x_pos_new = np.delete(x_pos_new, i)
            y_pos_new = np.delete(y_pos_new, i)
            matrix_new = np.delete(matrix_new, i, axis=0)
            matrix_new = np.delete(matrix_new, i, axis=1)

    return matrix_new, x_pos_new, y_pos_new





    
    
   