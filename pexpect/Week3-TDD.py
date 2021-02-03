import netmiko

class Router:
    """Represent router in environment"""

    def __init__(self, ipAddress, hostName, vendor):
        """Object initialization"""
        self.ipAddress = ipAddress
        self.hostName = hostName
        self.vendor = vendor
        self.interface = []
        self.neighbor = {}

    def add_interface(self, interface):
        """Add interface to interface dictionary"""
        self.interface.append(interface)
    
    def list_interface(self):
        """Listing interface of router"""
        return self.interface

    def neigbors_list(self):
        """Listing neighbor of router"""
        return self.neighbor

    def validate_interface(self, interface):
        """validate interface before take any action"""
        return interface in self.interface

    def connect_to(self, localInterface, remoteInterface, remoteHost):
        """Connect routers"""
        if self.validate_interface(localInterface):
            self.add_neighbor(neighborName=remoteHost, localInterface=localInterface, remoteInterface=remoteInterface)
        else:
            print("Error : Invalid interface")
            
    def add_neighbor(self, neighborName, localInterface, remoteInterface):
        if self.validate_interface(localInterface):
            if neighborName not in self.neighbor:
                self.neighbor[neighborName] = [{localInterface:remoteInterface}]
            else:
                self.neighbor[neighborName].append({localInterface:remoteInterface})
        else:
            print("Error: Invalid interface")
            
            

def main():
    """Main logic"""
    router_1 = Router("1.1.1.1", "router1", "cisco")
    router_1.add_interface("G1/0/1")
    router_1.add_interface("G1/0/2")
    router_2 = Router("2.2.2.2", "router2", "cisco")
    router_2.add_interface("G1/0/1")

    print(router_1.list_interface())

    connect("G1/0/1", router_1, "G1/0/1", router_2)

    print(router_1.neigbors_list())

def connect(localInterface, localhost, remoteInterface, remoteHost):

    localhost.connect_to(localInterface, remoteInterface, remoteHost.hostName)
    remoteHost.connect_to(remoteInterface, localInterface, localhost.hostName)


main()
    