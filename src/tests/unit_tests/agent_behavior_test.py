import unittest

from src.util.parser import load_parameters
from controller import Controller


def gen_agent():
    parameters = load_parameters("../test-setting.py")



    crtl = Controller(parameters=parameters)

    return crtl.sim.agents[0]


# Don't change the tests only the preparation when changing the API
class MyTestCase(unittest.TestCase):
    def test_something(self):
        try:
            agent = gen_agent()
        except:
            self.fail()


if __name__ == '__main__':
    unittest.main()
