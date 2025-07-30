from tightbinding.tbmodel import tbsquare, tbmodel
from tightbinding.tbcalculation import get_val_vec, ray_casting_method 
import numpy as np
from cmath import exp, sqrt
from math import pi

class tbsqure12(tbmodel):    
    '''
    Splice two tight-binding models together.
    '''
    def __init__(self, N, tb1, tb2, tb12, cut1, cut2=None, hermitian = True):
        '''
        tb1, tb2: tight-binding models
        cut1, cut2: the cut of the two tight-binding models.
        '''
        self.tb1 = tb1
        self.tb2 = tb2
        self.tb12 = tb12
        self.cut1 = cut1
        self.cut2 = cut2
        # 判断原胞是否在区域1内
        area1 = np.zeros(N*N)
        for i in range(N):
            for j in range(N):
                if ray_casting_method(i,j,cut1):
                    area1[i*N+j] = 1
        self.area1 = area1

        self.N = N
        self.N1 = np.sum(area1)
        self.N2 = N*N - self.N1
        self.n = self.tb1.n
        if self.tb1.n != self.tb2.n:
            print('Error: the number of atoms per unit cell in two tight-binding models are not equal.')
        self.hermitian = hermitian


    def get_H_OBC(self):
        H = self.hmatrix(self.n, self.N, self.N)
        
        for i in range(self.N):
            for j in range(self.N):
                if self.area1[i*self.N+j] == 1:
                    for item in self.tb1.coupling.keys():
                        i_new = i+item[0]
                        j_new = j+item[1]
                        try:
                            is_in_area1 = self.area1[i_new*self.N+j_new]
                        except IndexError:
                            continue
                        if is_in_area1 == 1:
                            H.set(self.tb1.coupling.get(item), i, j, item[0], item[1])
                        else:
                            try:
                                H.set(self.tb12.coupling.get(item), i, j, item[0], item[1])
                            except:
                                print(i,j,i_new,j_new,'Error1: the coupling is not defined in tb3.')
                elif self.area1[i*self.N+j] == 0:
                    for item in self.tb2.coupling.keys():
                        i_new = i+item[0]
                        j_new = j+item[1]
                        try:
                            is_in_area1 = self.area1[i_new*self.N+j_new]
                        except IndexError:
                            continue
                        if is_in_area1 == 0:
                            H.set(self.tb2.coupling.get(item), i, j, item[0], item[1])
                        else:
                            try:
                                H.set(self.tb12.coupling.get(item), i, j, item[0], item[1])
                            except:
                                print(i,j,i_new,j_new,'Error2: the coupling is not defined in tb3.')           
        return H.matrix + self.hermitian * H.matrix.conj().T


    def get_site_pos(self, boundary_condition='OBC', 
        position1=[(-0.3,-0.3), (0.3,-0.3), (-0.3,0.3), (0.3, 0.3)],
        position2=[(-0.2,-0.2), (0.2,-0.2), (-0.2,0.2), (0.2, 0.2)]):
        N = self.N
        x = np.empty(0)
        y = np.empty(0)
        if boundary_condition == 'OBC':
            for i in range(N):
                for j in range(N):
                    if self.area1[i*N+j] == 1:
                        position = position1
                    elif self.area1[i*N+j] == 0:
                        position = position2
                    for item in position:
                        x = np.append(x,i+item[0])
                        y = np.append(y,j+item[1])
        return x, y
    


class tbhexagonal12(tbsqure12):   
    '''
    cut切割按照base1, base2 坐标系而不是直角坐标系
    ''' 
    def __init__(self, N, tb1, tb2, tb12, cut1, cut2=None, hermitian = True,
                 base1=(sqrt(3)/2, 1/2), base2=(-sqrt(3)/2, 1/2)):
        super().__init__(N, tb1, tb2, tb12, cut1, cut2, hermitian)
        self.base1 = base1
        self.base2 = base2


    def get_site_pos(self, boundary_condition='OBC', 
        position1=[(exp(-1j*i*pi/3+1j*pi/2).real/3*1.1,exp(-1j*i*pi/3+1j*pi/2).imag/3*1.2) for i in range(6)],
        position2=[(exp(-1j*i*pi/3+1j*pi/2).real/3/1.1,exp(-1j*i*pi/3+1j*pi/2).imag/3/1.2) for i in range(6)]):
        N = self.N
        x = np.empty(0)
        y = np.empty(0)
        if boundary_condition == 'OBC':
            for i in range(N):
                for j in range(N):
                    if self.area1[i*N+j] == 1:
                        position = position1
                    elif self.area1[i*N+j] == 0:
                        position = position2
                    for item in position:
                        x = np.append(x,i*self.base1[0]+j*self.base2[0]+item[0].real)
                        y = np.append(y,i*self.base1[1]+j*self.base2[1]+item[1].real)
        return x.real, y.real





    
