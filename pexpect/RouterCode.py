import math
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

    def add_route(self, destinationNetwork, subnetMask, administrativeDistance, nextHopAddress=None, localInterface=None):
        """Add a route to routing table"""
        isIpValid = self.validate_route(destinationNetwork, subnetMask)
        destinationNetwork = self.calculate_network(destinationNetwork, subnetMask)
        try:
            administrativeDistance = int(administrativeDistance)
        except :
            print("Invalid administrative distance")
            return False
        if nextHopAddress != None and isIpValid:
            isNextHopValid = self.validate_next_hop(nextHopAddress)
            if isNextHopValid == False:
                return False
            self.routingTable[destinationNetwork] = {}
            self.routingTable[destinationNetwork]["SubnetMask"] = subnetMask
            self.routingTable[destinationNetwork]["NextHop"] = nextHopAddress
            self.routingTable[destinationNetwork]["AdministrativeDistance"] = administrativeDistance
            return True
        elif localInterface != None and isIpValid:
            isNextHopValid = self.validate_interface(localInterface)
            if isNextHopValid == False:
                return False
            self.routingTable[destinationNetwork] = {}
            self.routingTable[destinationNetwork]["SubnetMask"] = subnetMask
            self.routingTable[destinationNetwork]["NextHop"] = localInterface
            self.routingTable[destinationNetwork]["AdministrativeDistance"] = administrativeDistance
            return True
        else:
            return False
    def delete_route(self, network, subnetMask):
        network = self.calculate_network(network, subnetMask)
        if network in self.routingTable and self.routingTable[network]["SubnetMask"] == subnetMask:
            del self.routingTable[network]
            return True
        return False
    def calculate_network(self, ipAddress, subnetMask):
        ipAddress = ipAddress.split(".")
        subnetMask = subnetMask.split(".")
        if len(ipAddress) != 4 or len(subnetMask) != 4:
            return False
        network = ""
        for i in range(0, len(ipAddress)):
            network += str(int(ipAddress[i]) & int(subnetMask[i]))+("."*(i < (len(ipAddress)) - 1))
        return network

    def information(self):
        """Return a list of router's information"""
        return [self.hostName, self.ipAddress, self.vendor]

    def add_interface(self, interface):
        """Add interface to interface dictionary"""
        self.interface[interface] = {}
    def set_interface_address(self, localInterface, ipAddress, subnetMask):
        """Setup an ip address for interface"""
        if self.validate_ip_address(ipAddress, subnetMask) and self.validate_interface(localInterface):
            self.interface[localInterface]["Address"] = ipAddress
            self.interface[localInterface]["SubnetMask"] = subnetMask
            self.add_route(ipAddress, subnetMask, 1, localInterface=localInterface)
            return True
        else:
            return False
    def validate_next_hop(self, nextHopAddress):
        """Validate netx hop address"""
        nextHopAddress = nextHopAddress.split(".")
        if len(nextHopAddress) != 4:
            return False
        for octet in range(0, len(nextHopAddress)):
            temp_octet = int(octet)
            if temp_octet > 255 or temp_octet < 0:
                return False
        return True
    def validate_route(self, route, subnetMask):
        """Validate route"""
        route = route.split('.')
        subnetMask = subnetMask.split('.')
        if len(route) != 4 or len(subnetMask) != 4:
            return False
        for address in range(0, len(route)):
            try:
                tempRoute = int(route[address])
                tempSubnetMask = int(subnetMask[address])
            except:
                return False
            else:
                if (tempRoute > 255) or (tempRoute < 0):
                    return False
                elif tempSubnetMask == 255 or tempSubnetMask == 0:
                    if address == len(route) - 1:
                        return True
                    else:
                        continue
                elif (tempRoute & tempSubnetMask) != tempRoute:
                    return False
                else:
                    continue
        return True
        
    def validate_ip_address(self, ipAddress, subnetMask):
        """Validate the ip address"""
        ipAddress = ipAddress.split('.')
        subnetMask = subnetMask.split('.')
        if len(ipAddress) != 4 or len(subnetMask) != 4:
            return False
        for address in range(0, len(ipAddress)):
            try:
                tempIpAddress = int(ipAddress[address])
                tempSubnetMask = int(subnetMask[address])
            except:
                print("Can't parse ip address or subnet")
                return False
            else:
                if (tempIpAddress > 255) or (tempIpAddress < 0) :
                    print("Invalid ip range")
                    return False
                elif tempSubnetMask == 255:
                    continue
                elif ((tempIpAddress // (256 - tempSubnetMask)) * (256 - tempSubnetMask) + \
                    (256 - tempSubnetMask) - 1) == tempIpAddress:
                    return False
                else:
                    continue
        return True
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
            self.add_neighbor(neighborName=remoteHost, localInterface=localInterface, \
            remoteInterface=remoteInterface)
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
    router_1.set_interface_address("G1/0/1", "10.0.0.1", "255.255.255.0")
    router_1.calculate_network("192.168.1.1", "255.255.255.0")
    router_1.add_route("192.168.20.1", "255.255.0.0", 20, nextHopAddress="10.0.0.1")
    router_1.delete_route("192.168.0.0", "255.255.255.0")
    print(router_1.routing_table_list())
    


def connect(localInterface, localhost, remoteInterface, remoteHost):
    """Connect router to each other"""
    
    if localhost.validate_interface(localInterface) and remoteHost.validate_interface(remoteInterface):
        res1 = localhost.connect_to(localInterface, remoteInterface, remoteHost.hostName)
        res2 = remoteHost.connect_to(remoteInterface, localInterface, localhost.hostName)
        return res1 and res2
    return False

def disconnect(localInterface, localHost,remoteInterface, remoteHost):
    
    if localHost.is_connected_to(remoteHost.hostName, localInterface) and \
        remoteHost.is_connected_to(localHost.hostName, remoteInterface):
        res1 = localHost.disconnect_to(localInterface, remoteHost.hostName)
        res2 = remoteHost.disconnect_to(remoteInterface, localHost.hostName)
        return res1 and res2
    return False
    
if __name__=='__main__':
    main()
    