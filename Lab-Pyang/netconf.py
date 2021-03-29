# import requests
from ncclient import manager
import xmltodict
import pprint
import json
def main():
    mgr = manager.connect(host="10.0.15.196", port=430, username="admin", password="cisco", hostkey_verify=False)
    # for capability in mgr.server_capabilities:
    #     print(capability)
    
    netconf_loopback = """
        <filter>
            <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces" />
        </filter>
    """
    netconf_filter = """
        <filter>
            <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>GigabitEthernet1</name>
                </interface>
            </interfaces-state>
        </filter>
    """
    # config = mgr.edit_config(target="running", config=netconf_loopback)
    data = mgr.get(filter=netconf_filter).data_xml
    pprint.pprint(xmltodict.parse(data,dict_constructor=dict))
    # print(data)
main()