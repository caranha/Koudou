import abc

from .id_generator import IdGen


class SimulationElement(abc.ABC):
    """

    Abstract Base Class of Interface to synchronize all elements of the simulation

    """

    update_attr = {}

    def __init__(self):
        self.__generatePrivateAtrributes__()
        self.id = IdGen()

    def __hash__(self):
        return hash(self.id)

    def __call__(self):
        self.step()

    def __getattribute__(self, attr):
        privattr = "_" + attr
        return object.__getattribute__(self,privattr)

    def __getattr__(self, item):
        return object.__getattribute__(self, item)

    def __generatePrivateAtrributes__(self):
        for attr in list(self.__dict__.keys()):
            if not attr.startswith("_"):
                privattr = "_" + attr
                self.__dict__[privattr] = self.__dict__[attr]


    @abc.abstractmethod
    def step(self):
        pass

    def __update__(self):
        for attr in list(self.__dict__.keys()):
            if attr.startswith("_"):
                if attr[1:] in self.update_attr.keys():
                    self.__dict__[attr[1:]] += self.update_attr[attr[1:]]
                self.__dict__[attr] = self.__dict__[attr[1:]]


