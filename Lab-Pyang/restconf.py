import requests
import pprint
def main():
    url = "https://10.0.15.196:443"
    capability = '/restconf/operation/Cisco-IOS-XE-native/'
    header = {"Content-Type":"application/yang-data+json", "Accept":"application/yang-data+json"}
    payload = {"ietf-interfaces:interface": {'name':"Loopback1","description":"Test", 'type':"iana-if-type:softwareLoopback","enabled":'true',"ietf-ip:ipv4":{"address":[{"ip":"1.1.1.1", "netmask":"255.255.255.255"}]}}}
    # response_2 = requests.patch(url+capability, headers=header, auth=("admin", "cisco"), verify=False, json=payload)
    response = requests.get(url+capability, headers=header, auth=("admin", "cisco"), verify=False)
    # response_3 = requests.put(url+capability, json=payload, auth=("admin", 'cisco'), verify=False, headers=header)
    # print(response)
    pprint.pprint(response)
    # pprint.pprint(response_2.status_code)
main()