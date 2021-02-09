import pexpect

class Router:
    """This class represent managed router"""
    def __init__(self, ipAddress, name):
        """Object Initialization"""
        self.ipAddress = ipAddress
        self.name = name
        self.username = "admin"
        self.password = "cisco"
        self.prompt = self.name+"#"
        
    def sendCommand(self):
        child = pexpect.spawn('telnet {}'.format(self.ipAddress))
        child.expect("Username")
        child.sendline(self.username)
        child.expect("Password")
        child.sendline(self.password)
        child.expect(self.prompt)
        result = child.before
        print(result)
        child.sendline('end\nexit')
def main():
    router1 = Router("172.31.179.4", "R1")
    router1.sendCommand()
main()

