import netmiko
import re as regex
import os 
import time

from netmiko.ssh_dispatcher import ConnectHandler

class managedDevice:
    """Represent router in environment"""

    def __init__(self, ipAddress, hostName=None, vendor=None, deviceType=None):
        """Object initialization"""
        self.hostName = hostName
        self.managementAddress = ipAddress
        self.managementPort = {} #{controllerLocalPort:remotePort}
        self.interface = {}
        self.neighbor = {}
        self.deviceType = deviceType
        self.connectionTemplate = {'device_type':'cisco_ios', 'host':str(self.managementAddress), \
        'username':"admin", 'password':"cisco", 'port':22, 'blocking_timeout':20}
        self.filePath = os.path.dirname(os.path.realpath(__file__))+"\\\\DeviceConfiguration\\\\{}.txt".format(self.hostName)
        self.initialize_device_configuration()
        self.backup_device_configuration()
    
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
            save_ouconnection.send_command("cop run run.bkup", expect_string='Destination filename')
            # connection.send_command("\n", expect_string='#')
            # print(rollbackScriptScheduler)
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
    def configure_device(self, command):
        """Configure Remote Device"""
        if self.rollback_configuration_safeguard():
            try:
                connection = netmiko.ConnectHandler(**self.connectionTemplate)
            except :
                print("Faied to configured device {}".format(self.hostName))
                return False
            else:
                commandList = command.split('\n')
                for cmd in commandList:
                    connection.send_command(cmd, expect_string=r'#')
                connection.save_config()
                self.remove_configuration_safeguard()
                connection.disconnect()
        else:
            return False
    def get_remote_configuration(self):
        """Get remote configuration"""
        try:
            connection = netmiko.ConnectHandler(**self.connectionTemplate)
        except:
            print("Unable to open connection")
            return False
        else:
            configuration = connection.send_command("show run")
            connection.disconnect()
            return configuration
    def save_configuration(self, saveFileName='run.bkup'):
        """Custom save configuration file"""
        connection = self.open_connection()
        if connection != False:
            save_command = ["copy run {}".format(saveFileName)]
            


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
    managedDeviceDatabase = []
    devices = discover_device(managementAddress, "admin", 'cisco')
    for device in devices:
        managedDeviceDatabase.append(managedDevice(devices[device]["ManagementAddress"], device, deviceType="Cisco"))
    print(managedDeviceDatabase[0].hostName)
    managedDeviceDatabase[0].configure_device("conf t\nip vrf jubby")
    
    

def discover_device(controllerAddress, username, password, port=22,deviceType='cisco_ios', secret=''):
    """Discovery network device and return collection of devices connected to controller"""
    controller = {'device_type':deviceType, 'host':str(controllerAddress), \
    'username':username, 'password':password, 'port':port}
    connection = netmiko.ConnectHandler(**controller)
    devices = connection.send_command("show cdp neighbor").split("\n")
    database = {}
    for i in range(6, len(devices)-2):
        data = devices[i].split()
        database[data[0]] = {}
        database[data[0]]["LocalInterface"] = data[1]+data[2]
        database[data[0]]["RemoteInterface"] = data[6]+data[7]
        database[data[0]]["DeviceType"] = "Router" if data[4] == "R" else "Switch"
        managementAddress = connection.send_command("show cdp entry {} | section Management".format(data[0]))
        managementAddress = regex.findall("[0-9]*\.[0-9]*\.[0-9]*.[0-9]{1,3}", managementAddress)
        database[data[0]]["ManagementAddress"] = managementAddress[0]
    connection.disconnect()
    return database
    

if __name__=='__main__':
    main()
    