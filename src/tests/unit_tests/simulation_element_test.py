import unittest


from ...util.simulation_element import SimulationElement



class StepExecuted(Exception):
    pass

class FixtureClass(SimulationElement):
    def __init__(self):
        self.a = 'a'
        self.b = 'b'
        self.c = 'c'
        super().__init__()

    def step(self):
        raise StepExecuted()




class SimulationElementTest(unittest.TestCase):
    def test_abstract_class(self):
            with self.assertRaises(TypeError):
                SimulationElement()

    def test_instance(self):
        try:
            FixtureClass()
        except:
            self.fail("Couldn't instantiate object!")

    def test_id_generated(self):
        instance = FixtureClass()
        self.assertIn('id', instance.__dict__.keys())

    def test_priv_attr_generated(self):
        instance = FixtureClass()

        for letter in ['a', 'b', 'c']:
            self.assertIn('_' + letter, instance.__dict__.keys())

    def test_sync_attr(self):
        instance = FixtureClass()
        a1 = 'a'
        a2 = 'aa'

        self.assertEqual(instance.a, a1)

        instance.a = a2

        self.assertEqual(instance.a, a1)

        instance.__update__()

        self.assertEqual(instance.a, a2)

    def test_callable_step(self):
        with self.assertRaises(StepExecuted):
            instance = FixtureClass()
            instance()


if __name__ == '__main__':
    unittest.main()
