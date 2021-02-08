import unittest
from RouterCode import *
# from RouterCode import Router

class Router_Test(unittest.TestCase):
    def test_interface_list(self):
        router = Router('1.1.1.1', 'Router-1', 'cisco')
        router.add_interface("G1/0/1")
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
        self.assertDictEqual(router_1.routing_table_list(), {})
    def test_disconnect(self):
        router_1 = Router('1.1.1.1', 'Router-1', 'cisco')
        router_2 = Router('2.2.2.2.', "Router-2", "cisco")
        router_1.add_interface("G1/0/1")
        router_2.add_interface("G1/0/2")
        connect("G1/0/1", router_1, "G1/0/2", router_2)
        response = disconnect("G1/0/1", router_1,"G1/0/2", router_2)
        self.assertTrue(response)
        connect("G1/0/1", router_1, "G1/0/2", router_2)
        response = disconnect("G1/0/1", router_1, "G1/0/1", router_2)
        self.assertFalse(response)
    def test_interface_address(self):
        router_1 = Router("1.1.1.1", "router_1", "Aruba")
        router_1.add_interface("G1/0/1")
        response = router_1.set_interface_address("G1/0/1", "192.168.1.1", "255.255.255.0")
        self.assertTrue(response)
        self.assertDictEqual(router_1.interface_list(), {"G1/0/1":{"Address":"192.168.1.1", "SubnetMask":"255.255.255.0"}})
if __name__=='__main__':
    unittest.main()