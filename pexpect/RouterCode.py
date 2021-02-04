import netmiko
import unittest

class Router:
    """Represent router in environment"""

    def __init__(self, ipAddress, hostName, vendor):
        """Object initialization"""
        self.ipAddress = ipAddress
        self.hostName = hostName
        self.vendor = vendor
        self.interface = {}
        self.neighbor = {}
        self.routingTable = []

    def routing_table_list(self):
        """Listing routing tables"""
        return self.routingTable
    def add_route(self, destinationNetwork, nextHop):
        """Add a route to routing table"""
        
        
    def add_interface(self, interface):
        """Add interface to interface dictionary"""
        self.interface[interface] = {}
    
    def interface_list(self):
        """Listing interface of router"""
        return self.interface

    def neigbors_list(self):
        """Listing neighbor of router"""
        return self.neighbor
    def validate_interface(self, interface):
        """validate interface before take any action"""
        print(self.interface)
        return interface in self.interface
    def connect_to(self, localInterface, remoteInterface, remoteHost):
        """Connect routers"""
        if self.validate_interface(localInterface):
            self.add_neighbor(neighborName=remoteHost, localInterface=localInterface, remoteInterface=remoteInterface)
            return True
        else:
            return False
    def add_neighbor(self, neighborName, localInterface, remoteInterface):
        """Neighbor"""
        if self.validate_interface(localInterface):
            if neighborName not in self.neighbor:
                self.neighbor[neighborName] = [{localInterface:remoteInterface}]
            else:
                self.neighbor[neighborName].append({localInterface:remoteInterface})
        else:
            print("Error: Invalid interface")
    def remove_neighbor(self, neighborName, localInterface, remoteInterface):
        """Removing connected neighbor"""
            
            

def main():
    """Main logic"""
    # router_1 = Router("1.1.1.1", "router1", "cisco")
    # router_1.add_interface("G1/0/1")
    # router_1.add_interface("G1/0/2")
    # router_2 = Router("2.2.2.2", "router2", "cisco")
    # router_2.add_interface("G1/0/1")

    # # print(router_1.interface_list())

    # connect("G1/0/2", router_1, "G1/0/1", router_2)

    # print(router_1.neigbors_list())
    # print(router_2.neigbors_list())


def connect(localInterface, localhost, remoteInterface, remoteHost):

    res1 = localhost.connect_to(localInterface, remoteInterface, remoteHost.hostName)
    res2 = remoteHost.connect_to(remoteInterface, localInterface, localhost.hostName)
    return res1 and res2

main()
    