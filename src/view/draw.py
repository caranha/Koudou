import numpy as np

class Draw():
    def __init__(self):
        pass

class Transform():
    def __init__(self):
        self.mat = np.identity(3)

    def reset(self):
        self.mat = np.identity(3)

    def _rotate(self, theta):
        pass

    def rotate(self, px, py, theta):
        #translate
        #rotate
        #translate back
        pass


    def translate(self, dx, dy):
        self.mat[0][2] += dx
        self.mat[1][2] += dy

    def scale(self, sx, sy):
        self.mat[0][0] *= sx
        self.mat[1][1] *= sy

        self.mat[0][2] *= sx
        self.mat[1][2] *= sy

    def apply(self, x, y):
        return np.matmul(self.mat, [x, y, 1])[:2]

class ViewPort():
    def __init__(self, height, width, wmin, wmax, x=0, y=0, s=100000):
        # todo proper python  get/set
        self.x = x
        self.y = y

        self.height = height
        self.width = width

        self.wmin = wmin
        self.wmax = wmax

        self.s = s

        self.__transform = Transform()
        self.__compute()

    def __compute(self):
        self.__transform.reset()
        self.__transform.translate(-self.wmin[0], -self.wmin[1])
        self.__transform.scale(1, -1)

        self.__transform.scale(self.s, self.s)
        # fit map
        # cw = self.width/(self.wmax[1]-self.wmin[1])
        # ch = self.height/(self.wmax[0]-self.wmin[0])
        # self.__transform.scale(cw, ch)

        # self.__transform.translate(self.x, self.y)
        self.__transform.translate(500, 4000) #hack, adjust later

        #print(self.x, self.y)

    def change_scale(self, s):
        self.s = s
        self.__compute()

    def update_scale(self, s):
        self.s += s
        self.__compute()

    def change_center(self, x, y):
        self.x = x
        self.y = y
        self.__compute()

    def update_center(self, dx, dy):
        # deprecated
        # tx = min(0, tx) #if(self.view_port[0] > 0):  self.view_port = (0, self.view_port[1])
        # ty = min(0, ty) #if(self.view_port[1] > 0): self.view_port = (self.view_port[0], 0)
        # deprecated, equivalent to
        # tx = max(tx, -1*self.s*self.wmax[0] + self.width)
        # ty = max(ty, -1*self.s*self.wmax[1] + self.height)

        self.x = self.x - dx
        self.y = self.y - dy
        self.__compute()

    def apply(self, x, y):
        return self.__transform.apply(x, y)

    def __deprecated_trans_lon(self, lon):
        # trans_lon = lambda lon: (lon - self.canvasOrigin[0]) * self.scale + self.view_port[0]
        return (lon - self.wmin[0])*self.s + self.x
    def __deprecated_trans_lat(self, lat):
        # trans_lat = lambda lat: (self.canvasSize[1]-(lat - self.canvasOrigin[1])) * self.scale + self.view_port[1]
        return (self.wmax[1]-(lat-self.wmin[1])) * (self.s+self.y)

class Camera():
    def __init__(self):
        self.transform = Transform()
