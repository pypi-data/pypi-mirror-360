import numpy as np
from cmath import exp, sqrt
from math import pi
import math


class tbmodel:
    def __init__(self,n, N=10, hermitian = True):
        self.hermitian: bool = hermitian
        self.n: int = n
        self.N: int = N
        # 这里的（0,1）对应到array是axis=0的耦合
        # 注意数学坐标系与np.ndarray的不符，imshow与plotly.scatter的不符
        self.coupling: dict = {
            (0,0): np.zeros((n,n))*0j, 
        }


    def add_coupling(self, unit_to=(0,0), atom_from = 0, atom_to = 0, value = 0):
        if unit_to not in self.coupling.keys():
            self.coupling.update({unit_to: np.zeros((self.n,self.n))*0j})
        self.coupling.get(unit_to)[atom_from, atom_to] += value
   
    
    class hmatrix:
        '''
        哈密顿矩阵对象
        set()为了避免耦合超出边界
        '''
        def __init__(self, n, imax, jmax):
            self.matrix: np.ndarray = np.zeros((n*imax*jmax, n*imax*jmax))*0j
            self.imax: int = imax
            self.jmax: int = jmax
            self.n: int = n
        
        def set(self, sub_matrix, i, j, delta_i, delta_j):
            if (i+delta_i) >= 0 and (i+delta_i) < self.imax and \
                (j+delta_j) >= 0 and (j+delta_j) < self.jmax:
                unit_ind = i*self.jmax + j
                unit_delta_ind = (i+delta_i)*self.jmax + (j+delta_j)
                self.matrix[
                    unit_ind*self.n: unit_ind*self.n + self.n,
                    unit_delta_ind*self.n: unit_delta_ind*self.n + self.n
                ] += sub_matrix



class tbsquare(tbmodel):

    def get_H_PBC(self, kx, ky):
        H_PBC = np.zeros((self.n, self.n))*0j
        for item in self.coupling.keys():
            H_PBC += self.coupling.get(item) * exp(1j*item[0]*kx) * exp(1j*item[1]*ky)
        return H_PBC + self.hermitian * H_PBC.conj().T 
    

    def get_H_xPBC(self, kx):
        H_xPBC = self.hmatrix(self.n, 1, self.N)
        for j in range(self.N):
            for item in self.coupling.keys():
                smatrix = self.coupling.get(item) * exp(1j*item[0]*kx)
                # j 的方向为周期，不会超出边界，令delta_j=0
                H_xPBC.set(smatrix, 0, j, 0, item[1])
        return H_xPBC.matrix + self.hermitian * H_xPBC.matrix.conj().T
    

    def get_H_xyPBC(self, kx):
        '''
        斜切45度角的周期边界条件
        '''
        H_xPBC = self.hmatrix(self.n, 1, self.N)
        for j in range(self.N):
            for item in self.coupling.keys():
                smatrix = self.coupling.get(item) * exp(1j*item[0]*kx)
                # j 的方向为周期，不会超出边界，令delta_j=0
                H_xPBC.set(smatrix, 0, j, 0, item[1]-item[0])
        return H_xPBC.matrix + self.hermitian * H_xPBC.matrix.conj().T
    

    def get_H_OBC(self):
        H_OBC = self.hmatrix(self.n, self.N, self.N)
        for i in range(self.N):
            for j in range(self.N):
                for item in self.coupling.keys():
                    H_OBC.set(self.coupling.get(item), i, j, item[0], item[1])
        return H_OBC.matrix + self.hermitian * H_OBC.matrix.conj().T


    def get_site_pos(self, boundary_condition='OBC', position=[(-0.25,-0.25), (0.25,-0.25), (-0.25,0.25), (0.25, 0.25)]):
        N = self.N
        x = np.empty(0)
        y = np.empty(0)
        if boundary_condition == 'PBC':
            for item in position:
                x = np.append(x,item[0])
                y = np.append(y,item[1])
        elif boundary_condition in ['xPBC', 'xyPBC']:
            for j in range(N):
                for item in position:
                    x = np.append(x,item[0])
                    y = np.append(y,j+item[1])
        elif boundary_condition == 'OBC':
            for i in range(N):
                for j in range(N):
                    for item in position:
                        x = np.append(x,i+item[0])
                        y = np.append(y,j+item[1])
        else:
            print('boundary_condition should be one of [PBC, xPBC, OBC].')
            return
        return x, y
    




class tbhexagonal(tbmodel):
    def __init__(self,n, N=10, hermitian = True, 
        base1=(sqrt(3)/2, 1/2), base2=(-sqrt(3)/2, 1/2)
    ):
        super().__init__(n, N, hermitian)
        self.base1 = base1
        self.base2 = base2


    def get_H_PBC(self, kx, ky):
        H_PBC = np.zeros((self.n, self.n))*0j
        for item in self.coupling.keys():
            ax = item[0]*self.base1[0] + item[1]*self.base2[0]
            ay = item[0]*self.base1[1] + item[1]*self.base2[1]
            H_PBC += self.coupling.get(item) * exp(1j*ax*kx) * exp(1j*ay*ky)
        return H_PBC + self.hermitian * H_PBC.conj().T
    

    def get_H_zigzag(self, k1):
        H_xPBC = self.hmatrix(self.n, 1, self.N)
        i = 0
        for j in range(self.N):
            for item in self.coupling.keys():
                smatrix = self.coupling.get(item) * exp(1j*item[0]*k1)
                # j 的方向为周期，不会超出边界，令delta_j=0
                H_xPBC.set(smatrix, i, j, 0, item[1])
        return H_xPBC.matrix + self.hermitian * H_xPBC.matrix.conj().T


    def get_H_armchair(self, k1):
        H_xPBC = self.hmatrix(self.n, 1, self.N)
        for j in range(self.N):
            for item in self.coupling.keys():
                smatrix = self.coupling.get(item) * exp(1j*item[0]*sqrt(3)*k1)
                H_xPBC.set(smatrix, 0, j, 0, item[1]+item[0])
        return H_xPBC.matrix + self.hermitian * H_xPBC.matrix.conj().T
    

    def get_H_bearded(self, k1):
        H_xPBC = self.hmatrix(self.n, 1, self.N)
        for j in range(self.N):
            for item in self.coupling.keys():
                smatrix = self.coupling.get(item) * exp(1j*item[0]*k1)
                H_xPBC.set(smatrix, 0, j, 0, item[1]-item[0])
        return H_xPBC.matrix + self.hermitian * H_xPBC.matrix.conj().T


    def get_H_OBC(self):
        H_OBC = self.hmatrix(self.n, self.N, self.N)
        for i in range(self.N):
            for j in range(self.N):
                for item in self.coupling.keys():
                    H_OBC.set(self.coupling.get(item), i, j, item[0], item[1])
        return H_OBC.matrix + self.hermitian * H_OBC.matrix.conj().T


    def get_site_pos(self, boundary_condition='OBC', position=[(-sqrt(3)/6,0), (sqrt(3)/6,0)]):
        N = self.N
        x = np.empty(0)
        y = np.empty(0)
        if boundary_condition == 'PBC':
            for item in position:
                x = np.append(x,item[0])
                y = np.append(y,item[1])
        elif boundary_condition in ['zigzag', 'armchair', 'bearded']:
            for j in range(N):
                for item in position:
                    x = np.append(x,j*self.base2[0]+item[0])
                    y = np.append(y,j*self.base2[1]+item[1])
        elif boundary_condition == 'OBC':
            for i in range(N):
                for j in range(N):
                    for item in position:
                        x = np.append(x,i*self.base1[0]+j*self.base2[0]+item[0])
                        y = np.append(y,i*self.base1[1]+j*self.base2[1]+item[1])
        else:
            print('boundary_condition should be one of [PBC, xPBC, OBC].')
            return
        return x, y
    


class tbmodel3D:
    def __init__(self,n, N=10, hermitian = True):
        self.hermitian: bool = hermitian
        self.n: int = n
        self.N: int = N
        self.coupling: dict = {
            (0,0,0): np.zeros((n,n))*0j, 
        }


    def add_coupling(self, unit_to=(0,0,0), atom_from = 0, atom_to = 0, value = 0):
        if unit_to not in self.coupling.keys():
            self.coupling.update({unit_to: np.zeros((self.n,self.n))*0j})
        self.coupling.get(unit_to)[atom_from, atom_to] += value
   
    
    class hmatrix:
        '''
        哈密顿矩阵对象
        set()为了避免耦合超出边界
        '''
        def __init__(self, n, imax, jmax, lmax):
            self.matrix: np.ndarray = np.zeros((n*imax*jmax*lmax, n*imax*jmax*lmax))*0j
            self.imax: int = imax
            self.jmax: int = jmax
            self.lmax: int = lmax
            self.n: int = n
        
        def set(self, sub_matrix, i, j, l, delta_i, delta_j, delta_l):
            if (i+delta_i) >= 0 and (i+delta_i) < self.imax and \
                (j+delta_j) >= 0 and (j+delta_j) < self.jmax and \
                (l+delta_l) >= 0 and (l+delta_l) < self.lmax:
                unit_ind = i*self.jmax*self.lmax + j*self.lmax + l
                unit_delta_ind = (i+delta_i)*self.jmax*self.lmax + (j+delta_j)*self.lmax + l+delta_l
                self.matrix[
                    unit_ind*self.n: unit_ind*self.n + self.n,
                    unit_delta_ind*self.n: unit_delta_ind*self.n + self.n
                ] += sub_matrix



class tbsquare3D(tbmodel3D):

    def get_H_PBC(self, kx, ky, kz):
        H_PBC = np.zeros((self.n, self.n))*0j
        for item in self.coupling.keys():
            H_PBC += self.coupling.get(item) * exp(1j*item[0]*kx) * exp(1j*item[1]*ky) * exp(1j*item[2]*kz)
        return H_PBC + self.hermitian * H_PBC.conj().T 


    def get_H_xPBC(self, kx):
        H_xPBC = self.hmatrix(self.n, 1, self.N, self.N)
        for j in range(self.N):
            for l in range(self.N):
                for item in self.coupling.keys():
                    smatrix = self.coupling.get(item) * exp(1j*item[0]*kx)
                    H_xPBC.set(smatrix, 0, j, l, 0, item[1], item[2])
        return H_xPBC.matrix + self.hermitian * H_xPBC.matrix.conj().T
     

    def get_H_OBC(self):
        H_OBC = self.hmatrix(self.n, self.N, self.N, self.N)
        for i in range(self.N):
            for j in range(self.N):
                for l in range(self.N):
                    for item in self.coupling.keys():
                        H_OBC.set(self.coupling.get(item), i, j, l, item[0], item[1], item[2])
        return H_OBC.matrix + self.hermitian * H_OBC.matrix.conj().T


    def get_site_pos(self, boundary_condition='OBC', 
            position=[(-0.25,-0.25,-0.25), (0.25,-0.25,-0.25), (-0.25,0.25,-0.25), (0.25, 0.25,-0.25),
                      (-0.25,-0.25,0.25), (0.25,-0.25,0.25), (-0.25,0.25,0.25), (0.25, 0.25,0.25)]):
        N = self.N
        x = np.empty(0)
        y = np.empty(0)
        z = np.empty(0)
        if boundary_condition == 'PBC':
            for item in position:
                x = np.append(x,item[0])
                y = np.append(y,item[1])
                z = np.append(z,item[2])

        elif boundary_condition in ['xPBC']:
            for j in range(N):
                for l in range(N):
                    for item in position:
                        x = np.append(x,item[0])
                        y = np.append(y,j+item[1])
                        z = np.append(z,l+item[2])
        elif boundary_condition == 'OBC':
            for i in range(N):
                for j in range(N):
                    for l in range(N):
                        for item in position:
                            x = np.append(x,i+item[0])
                            y = np.append(y,j+item[1])
                            z = np.append(z,l+item[2])
        
        else:
            print('boundary_condition should be one of [PBC, xPBC, OBC].')
            return

        return x, y, z
