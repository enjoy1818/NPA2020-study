# import requests
from ncclient import manager
def main():
    mgr = manager.connect(host="10.0.15.196", port=830, username="admin", password="cisco", hostkey_verify=False)
    # for capability in mgr.server_capabilities:
    #     print(capability)
    
    netconf_loopback = """
        <config>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
        <Loopback operation="delete">
        <name>2</name>
        </Loopback>
        </interface>
        </native>
        </config>
    """
    config = mgr.edit_config(target="running", config=netconf_loopback)
    print(config)
main()