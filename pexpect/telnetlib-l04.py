import getpass
import telnetlib
import time

class Router:
    """This class represent managed router"""
    def __init__(self, ipAddress, name):
        """Object Initialization"""
        self.ipAddress = ipAddress
        self.name = name
        self.username = "admin"
        self.password = "cisco"

    def setupConnection(self):
        self.connection = telnetlib.Telnet(self.ipAddress, 23, 5)
        self.connection.read_until(b"Username:")
        self.connection.write(self.username.encode('ascii')+b'\n')
        time.sleep(1)
        self.connection.read_until(b"Password:")
        self.connection.write(self.password.encode('ascii')+b'\n')      

    def closeConnection(self):
        self.connection.close()

router1 = Router("172.31.179.4", "R1")
router1.setupConnection()
        