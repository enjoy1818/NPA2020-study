class Router:
    """Represent router in environment"""

    def __init__(self, ipAddress=None, hostName=None, vendor=None):
        """Object initialization"""
        self.ipAddress = ipAddress
        self.hostName = hostName
        self.vendor = vendor
        self.interface = {}
        self.neighbor = {}
        self.routingTable = {}

    def routing_table_list(self):
        """Listing routing tables"""
        return self.routingTable
    # def add_route(self, destinationNetwork, nextHop):
    #     """Add a route to routing table"""
        
    def information(self):
        """Return a list of router's information"""
        return [self.hostName, self.ipAddress, self.vendor]

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
        # print(interface in self.interface)
        return interface in self.interface
    def connect_to(self, localInterface, remoteInterface, remoteHost):
        """Connect routers"""
        if self.validate_interface(localInterface):
            self.add_neighbor(neighborName=remoteHost, localInterface=localInterface, remoteInterface=remoteInterface)
            return True
        else:
            return False
    def is_connected_to(self, remoteHost, localInterface=None):
        """Validating if this router is connected to designated host"""
        if remoteHost in self.neighbor:
            if localInterface != None and self.validate_interface(localInterface):
                for connectedInterface in self.neighbor[remoteHost]:
                    for interface in connectedInterface.keys():
                        if interface == localInterface:
                            return True
                        return False
            return True    
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
    def disconnect_to(self, localInterface, remoteHost):
        """Remove connection to another router"""
        if self.validate_interface(localInterface):
            if self.neighbor[remoteHost] != {}:
                for connectedInterface in self.neighbor[remoteHost]:
                    for interface in connectedInterface.keys():
                        if interface == localInterface:
                            connectedInterface.pop(interface)
                            return True
                    return False
                if self.neighbor[remoteHost] == [{}]:
                    self.remove_neighbor(remoteHost)
            return True
        else:
            return False
      
    def remove_neighbor(self, neighborName):
        """Remove neighbor"""
        self.neighbor.pop(neighborName)
        return "Neighbor {} removed".format(neighborName)
            
            

def main():
    """Main logic"""
    router_1 = Router("1.1.1.1", "router1", "cisco")
    router_1.add_interface("G1/0/1")
    router_1.add_interface("G1/0/2")
    router_2 = Router("2.2.2.2", "router2", "cisco")
    router_2.add_interface("G1/0/1")
    router_2.add_interface("G1/0/2")
    

    # # print(router_1.interface_list())

    print(connect("G1/0/2", router_1, "G1/0/1", router_2))

    print(router_1.neigbors_list())
    print(router_2.neigbors_list())

    print(disconnect("G1/0/2", router_1,"G1/0/1", router_2))

    print(router_1.neigbors_list())
    print(router_2.neigbors_list())


def connect(localInterface, localhost, remoteInterface, remoteHost):
    """Connect router to each other"""
    
    if localhost.validate_interface(localInterface) and remoteHost.validate_interface(remoteInterface):
        res1 = localhost.connect_to(localInterface, remoteInterface, remoteHost.hostName)
        res2 = remoteHost.connect_to(remoteInterface, localInterface, localhost.hostName)
        return res1 and res2
    return False

def disconnect(localInterface, localHost,remoteInterface, remoteHost):
    
    if localHost.is_connected_to(remoteHost.hostName, localInterface) and remoteHost.is_connected_to(localHost.hostName, remoteInterface):
        res1 = localHost.disconnect_to(localInterface, remoteHost.hostName)
        res2 = remoteHost.disconnect_to(remoteInterface, localHost.hostName)
        return res1 and res2
    return False
    
main()
    