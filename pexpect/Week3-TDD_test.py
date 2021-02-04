import unittest
from RouterCode import *
# from RouterCode import Router

class Router_Test(unittest.TestCase):
    def test_interface_list(self):
        router = Router('1.1.1.1', 'Router-1', 'cisco')
        router.add_interface("G1/0/1")
        # print(router.interface_list())
        self.assertEqual(router.interface_list(), {'G1/0/1':{}})
    def test_validate_interface(self):
        router = Router('1.1.1.1', 'Router-1', 'cisco')
        router.add_interface("G1/0/1")
        self.assertTrue(router.validate_interface('G1/0/1'))
        self.assertFalse(router.validate_interface('G1/0/2'))
    def test_connect(self):
        router_1 = Router('1.1.1.1', 'Router-1', 'cisco')
        router_2 = Router('2.2.2.2.', "Router-2", "cisco")
        router_1.add_interface("G1/0/1")
        router_2.add_interface("G1/0/2")
        self.assertFalse(connect("G1/0/2", router_1, "G1/0/1", router_2))
        self.assertTrue(connect("G1/0/1", router_1, "G1/0/2", router_2))
    def test_neighbor_list(self):
        router_1 = Router('1.1.1.1', 'Router-1', 'cisco')
        router_2 = Router('2.2.2.2.', "Router-2", "cisco")
        router_1.add_interface("G1/0/1")
        router_2.add_interface("G1/0/2")
        self.assertDictEqual(router_1.neigbors_list(), {})
        connect("G1/0/1", router_1, "G1/0/2", router_2)
        expectedResult = {'Router-2':[{'G1/0/1':'G1/0/2'}]}
        self.assertDictEqual(router_1.neigbors_list(), expectedResult)
    def test_routing_table_list(self):
        router_1 = Router('1.1.1.1', 'Router-1', "HPE")
        self.assertListEqual(router_1.routing_table_list(), [])
if __name__=='__main__':
    unittest.main()