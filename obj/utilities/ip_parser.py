#https://github.com/ftao/python-ifcfg

# try:
#     import ifcfg
# except ModuleNotFoundError:
#     pass
import socket
import json
from obj.utilities.utility_box import UtilityBox
from settings import NETWORK
from obj.utilities.exceptions import ServiceNotAvailableException

PUBLIC_IP_URL = 'http://jsonip.com'
class IpGetter(object):
    SERVICE_SERVERS_TABLE_DIRECTION = None

    @staticmethod
    def get_public_ip(raise_exception=False):
        public_ip = None
        try:
            public_ip = UtilityBox.do_request(PUBLIC_IP_URL)['ip']
        except NameError:
            print("Unable to get public IP") 
            if raise_exception:
                raise AssertionError("Unable to get public IP")
        return public_ip

    @staticmethod
    def get_local_ip(raise_exception=False):
        local_ip = None
        # try:  #Not working that well on windows
        #     #default = ifcfg.default_interface()    #Not working on windows
        #     for name, interface in ifcfg.interfaces().items():
        #         print(str(name)+':'+str(interface))
        # except (NameError, AssertionError):
        #     pass
        try:    #This private local ip can start with 10, not 192! Same shit, so no problems there.
            host_name = socket.gethostname() 
            host_ip = socket.gethostbyname(host_name) 
            local_ip = host_ip
        except:
            print("Unable to get local Hostname and IP")
            if raise_exception:
                raise AssertionError("Unable to get local Hostname and IP")
        return local_ip

    @staticmethod
    def get_servers_table_dir():
        """Detects the location of the node service that acts as a middleman for all the public connected users, be it clients or servers.
        First checks if the service is online in the amazon servers, and then 2 times if it is locally.
        Raises exception if no node script is dertected executing"""
        if not IpGetter.SERVICE_SERVERS_TABLE_DIRECTION:
            port_string = ':'+str(NETWORK.TABLE_SERVERS_PORT)
            table_servers_dir = NETWORK.TABLE_SERVERS_URL if UtilityBox.do_request(NETWORK.TABLE_SERVERS_URL+port_string, timeout=3, return_success_only=True)\
            else NETWORK.LOCAL_LOOPBACK_IP if UtilityBox.do_request(NETWORK.LOCAL_LOOPBACK_IP+port_string, timeout=3, return_success_only=True)\
            else NETWORK.LOCAL_IP if UtilityBox.do_request(NETWORK.LOCAL_IP+port_string, timeout=3, return_success_only=True)\
            else None
            # table_servers_dir = '127.0.0.1'
            if not table_servers_dir:
                raise ServiceNotAvailableException("A servide to register the servers was not detected, not online nor locally.")
            IpGetter.SERVICE_SERVERS_TABLE_DIRECTION = table_servers_dir+port_string
        return IpGetter.SERVICE_SERVERS_TABLE_DIRECTION

if __name__ == "__main__":
    print("My public ip is "+str(IpGetter.get_public_ip())+\
        " and my local network ip is "+str(IpGetter.get_local_ip()))
