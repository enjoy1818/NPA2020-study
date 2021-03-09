import netmiko
import re as regex
import os 
import time
import threading
import concurrent.futures
import pythonping
from netmiko.ssh_dispatcher import ConnectHandler

class managedDevice:
    """Represent router in environment"""

    def __init__(self, ipAddress=None, hostName=None, vendor=None, deviceType=None):
        """Object initialization"""
        self.hostName = hostName
        self.managementAddress = ipAddress
        self.managementPort = {} #{controllerLocalPort:remotePort}
        self.interface = {} #{interface:{"Name":"Interface Name", "Address":"Interface address", "Status":True/False}}
        self.neighbor = {}
        self.deviceType = deviceType
        self.connectionTemplate = {'device_type':'cisco_ios', 'host':str(self.managementAddress), \
        'username':"admin", 'password':"cisco", 'port':22, 'blocking_timeout':20}
        self.filePath = os.path.dirname(os.path.realpath(__file__))+"\\\\DeviceConfiguration\\\\{}.txt".format(self.hostName)
        # self.initialize_device_configuration()
        # self.backup_device_configuration()
    
    def initialize_device_configuration(self):
        """Device configuration management"""
        try:
            file = open(self.filePath, mode='x')
        except:
            return False
        else:
            file = open(self.filePath, mode='w')
        file.close()
        return True

    def backup_device_configuration(self):
        """Backup device configuration"""
        try:
            file = open(self.filePath, mode='w')
        except:
            return False
        else:
            configuration = self.get_remote_configuration()
            if type(configuration) == bool:
                print("Can't write")
            else:
                file.write(configuration)
            file.close()
            return True

    def rollback_configuration_safeguard(self, interval=2):
        """Create kron for rollback in case device is not response after configuration"""
        rollbackScriptPolicy = ["kron policy-list rollback-backup", "cli copy run.bkup run"]
        rollbackScriptScheduler = ["kron occur rollback in {} oneshot", "policy-list rollback-backup".format(str(interval).zfill(3))]
        try:
            connection = netmiko.ConnectHandler(**self.connectionTemplate)
        except :
            return False
        else:
            self.save_configuration()
            connection.send_command("conf t", expect_string=r'#')
            for command in rollbackScriptPolicy:
                connection.send_command(command, expect_string=r'#')
            for command in rollbackScriptScheduler:
                connection.send_command(command, expect_string=r'#')
            connection.disconnect()
            return True
            
    def remove_configuration_safeguard(self, interval=2):
        removeScript = ["conf t", " no kron occur rollback in {} oneshot".format(str(interval).zfill(3)), "no kron policy-list rollback-backup"]
        try:
            connection = netmiko.ConnectHandler(**self.connectionTemplate)
        except :
            return False
        else:
            for command in removeScript:
                connection.send_command(command, expect_string=r'#')
            connection.disconnect()
            return True

    def configure_device(self, designatedCommand):
        """Configure Remote Device"""
        if self.rollback_configuration_safeguard():
            try:
                connection = netmiko.ConnectHandler(**self.connectionTemplate)
            except :
                print("Faied to configured device {}".format(self.hostName))
                return False
            else:
                commandList = designatedCommand.split('\n')
                for command in commandList:
                    connection.send_command(command, expect_string=r"#")
                self.remove_configuration_safeguard()
                connection.disconnect()
                return True
        else:
            return False

    def interface_discovery(self):
        connection = self.open_connection()
        result = connection.send_command("show ip int brief", expect_string=r'#')
        connection.disconnect()
        for interface in result.split('\n')[1:]:
            interface_list = interface.split()
            self.interface[interface_list[0]] = {}
            self.interface[interface_list[0]]["Address"] = interface_list[1]
            self.interface[interface_list[0]]["Status"] = interface_list[4]+" "+interface_list[5]
        #  [self.interface[interface] for interface in result.split('\n')[1:]]
        return self.interface

    def enable_routing(self, routing_protocol, area=None, autonomous_system=None, vrf=None, default_route=False):
        self.interface_discovery()
        if routing_protocol == "OSPF":
            try:
                connection = self.open_connection()
            except:
                return False
            [connection.send_command(command, expect_string=r"#") for command in ["conf t", "router ospf 1 vrf jab", "end"]]
            connection.disconnect()
        for interface in self.interface:
            if self.interface[interface]["Address"] == "unassigned":
                continue
            else:
                connection = self.open_connection()
                [connection.send_command(command, expect_string=r"#") for command in ["conf t","int {}".format(interface),"ip ospf 1 area 0"]]
                connection.disconnect()
        return True

    def label_interface(self):
        connection = self.open_connection()
        devices = connection.send_command("show cdp neighbor").split("\n")
        for line_index in range(5, len(devices) - 2):
            # print(devices[line_index].split())
            neighbor = devices[line_index].split()
            connection = self.open_connection()
            [connection.send_command(command, expect_string=r'#') for command in ["conf t", "int {}".format(neighbor[1]+neighbor[2]), "desc connect to {} of {}".format(neighbor[6]+neighbor[7], neighbor[0].split(".")[0])]]
        # return devices
    def enable_cdp(self):
        connection = self.open_connection()
        [connection.send_command(command, expect_string=r"#") for command in ['conf t', 'cdp run']]
        # connection.send_command("conf t\ncdp run\nend\n", expect_string=r'#')
        connection.disconnect()
        return True

    def enable_lldp(self):
        connection = self.open_connection()
        [connection.send_command(command, expect_string=r"#") for command in ['conf t', 'lldp run']]
        # connection.send_command("conf t\nlldp run\nend\n", expect_string=r'#')
        connection.disconnect()
        return True

    def configure_interface(self, interface=None, status=None, address=None, subnet_mask=None):
        return True

    def get_remote_configuration(self):
        """Get remote configuration"""
        try:
            connection = netmiko.ConnectHandler(**self.connectionTemplate)
        except:
            print("Failed to get {} configuration".format(self.hostName))
            return False
        else:
            configuration = connection.send_command("show run")
            connection.disconnect()
            return configuration

    def save_configuration(self, saveFileName='run.bkup'):
        """Custom save configuration file"""
        connection = self.open_connection()
        if connection != False:
            testCommand = connection.send_command("dir flash0:/{}".format(saveFileName))
            if "Error" in testCommand:
                connection.send_command("copy run {}".format(saveFileName), expect_string=r"Destination")
                connection.send_command("\n", expect_string=r"#")
            else:
                connection.send_command("del {}".format(saveFileName), expect_string=r'Delete')
                connection.send_command("\n", expect_string=r'Delete')
                connection.send_command("\n", expect_string=r"#")
                connection.send_command("copy run {}".format(saveFileName), expect_string=r"Destination")
                connection.send_command("\n", expect_string=r"#")
            connection.disconnect()
            return True
        else:
            return False
            
    def health_check(self):
        """Health check device"""
        status = {}
        status["Hostname"] = self.hostName
        result = pythonping.ping(self.managementAddress, count=3)
        if "Reply" in str(result):
            status["Connectivity"] = True
        else:
            status["Connectivity"] = False
        test_connection = self.open_connection()
        if test_connection == False:
            status["SSH Connectivity"] = False
        else:
            status["SSH Connectivity"] = True

        return status

    def open_connection(self):
        try:
            connection = netmiko.ConnectHandler(**self.connectionTemplate)
        except :
            return False
        else:
            return connection
    
def main():
    """Main logic"""
    managementAddress = "172.31.179.2"
    managedDeviceDatabase = {}
    devices = discover_device(managementAddress, "admin", 'cisco')
    managedDeviceDatabase["S0"] = managedDevice(managementAddress, "S0.npa.com", vendor="Cisco")
    for device in devices:
        managedDeviceDatabase[device.split(".")[0]] = managedDevice(devices[device]["ManagementAddress"], device, vendor="Cisco")

    # Setup vrf and loopback interface
    print(send_command("conf t\nip vrf jab\nrd 300:69\n", managedDeviceDatabase))
    print([managedDeviceDatabase[device].health_check() for device in managedDeviceDatabase])
    print(send_command("conf t\nint lo 69\nip vrf forwarding jab\n", managedDeviceDatabase))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        workers = {executor.submit(lambda x: send_command(*x), ["conf t\nint lo69\nip vrf forwarding jab\nip address 172.20.179.{} {}"\
        .format(managedDeviceDatabase[device].managementAddress.split(".")[3], "255.255.255.240"), managedDeviceDatabase[device]]) for device in managedDeviceDatabase}

    # Increase SSH concurrent connection   
    send_command("conf t\nline vty 0 20\ntransport input ssh\nlogin local\n", managedDeviceDatabase)
    
    # Securing SSH 
    print(send_command("conf t\nip access-list standard ManagementAddress\npermit 172.31.179.0 0.0.0.15\npermit 10.253.190.0 0.0.0.255\n", managedDeviceDatabase))
    print(send_command("conf t\nline vty 0 20\naccess-class ManagementAddress in vrf-also\n", managedDeviceDatabase))

    # Configure interface
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(lambda x: send_command(*x), ["conf t\nvlan 69\nno shut\nname vrf-jab\n", managedDeviceDatabase["S1"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint range g0/1-2\nsw tr enc dot\nsw mode tr\n", managedDeviceDatabase["S1"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g1/0\nsw acc vlan 69\n", managedDeviceDatabase["S1"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nvlan 69\nno shut\nname vrf-jab\n", managedDeviceDatabase["S2"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint range g0/1-3\nsw tr enc dot\nsw mode tr\n", managedDeviceDatabase["S2"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/1.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.17 255.255.255.240\nint g0/1\nno shut\n", managedDeviceDatabase["R1"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/2.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.33 255.255.255.240\nint g0/2\nno shut\n", managedDeviceDatabase["R1"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/1.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.18 255.255.255.240\nint g0/1\nno shut\n", managedDeviceDatabase["R2"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/2.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.49 255.255.255.240\nint g0/2\nno shut\n", managedDeviceDatabase["R2"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/1.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.34 255.255.255.240\nint g0/1\nno shut\n", managedDeviceDatabase["R3"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/2.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.50 255.255.255.240\nint g0/2\nno shut\n", managedDeviceDatabase["R3"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/3.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.65 255.255.255.240\nint g0/3\nno shut\n", managedDeviceDatabase["R3"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/1.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.66 255.255.255.240\nint g0/1\nno shut\n", managedDeviceDatabase["R4"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/1.69\nip vrf forwarding jab\nenc dot 69\nip address 172.31.179.67 255.255.255.240\nint g0/1.69\nip nat enable\nno shut\n", managedDeviceDatabase["R5"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nint g0/2\nno shut\nip address dhcp\nip nat enable", managedDeviceDatabase["R5"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nip access-list standard NAT\npermit any", managedDeviceDatabase["R5"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nip route vrf jab 0.0.0.0 0.0.0.0 g0/2 192.168.122.1", managedDeviceDatabase["R5"]])
        executor.submit(lambda x: send_command(*x), ["conf t\nip nat source list NAT int g0/2 vrf jab overload", managedDeviceDatabase["R5"]])

    # # Enable ospf on active interface
    with concurrent.futures.ThreadPoolExecutor() as executor:
        workers = {executor.submit(managedDeviceDatabase[device].enable_routing, "OSPF") for device in managedDeviceDatabase}
    managedDeviceDatabase["R5"].enable_routing("OSPF", default_route=True)


    # Enable CDP and LLDP on device
    with concurrent.futures.ThreadPoolExecutor() as executor:
        workers_lldp = {executor.submit(managedDeviceDatabase[device].enable_lldp()) for device in managedDeviceDatabase}
        workers_cdp = {executor.submit(managedDeviceDatabase[device].enable_cdp()) for device in managedDeviceDatabase}
        
    # Labelling interfaces
    with concurrent.futures.ThreadPoolExecutor() as executor:
        workers_label = {executor.submit(managedDeviceDatabase[device].label_interface) for device in managedDeviceDatabase}
    
     
def send_command(command, devices):
    result = True
    if type(devices) == type(managedDevice()):
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        result = devices.configure_device(command)
            # result = executor.submit(devices.configure_device, command)
    elif type(devices) == type({}):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            workers = [executor.submit(devices[device].configure_device, command) for device in devices]
            workers_result = [worker.result() for worker in workers]
            if False in workers_result:
                result = False
    return result
    

def discover_device(controllerAddress, username, password, port=22,deviceType='cisco_ios', secret=''):
    """Discovery network device and return collection of devices connected to controller"""
    controller = {'device_type':deviceType, 'host':str(controllerAddress), \
    'username':username, 'password':password, 'port':port}
    connection = netmiko.ConnectHandler(**controller)
    devices = connection.send_command("show cdp neighbor").split("\n")
    connection.disconnect()
    database = {}
    for i in range(5, len(devices)-2):
        data = devices[i].split()
        database[data[0]] = {}
        database[data[0]]["LocalInterface"] = data[1]+data[2]
        database[data[0]]["RemoteInterface"] = data[6]+data[7]
        database[data[0]]["DeviceType"] = "Router" if data[4] == "R" else "Switch"
        connection = netmiko.ConnectHandler(**controller)
        managementAddress = connection.send_command("show cdp entry {} | section Management".format(data[0]))
        time.sleep(1)
        connection.disconnect()
        managementAddress = regex.findall("[0-9]*\.[0-9]*\.[0-9]*.[0-9]{1,3}", managementAddress)
        database[data[0]]["ManagementAddress"] = managementAddress[0]
    # connection.disconnect()
    return database
    

if __name__=='__main__':
    main()
    