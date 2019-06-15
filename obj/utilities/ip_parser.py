#https://github.com/ftao/python-ifcfg

# try:
#     import ifcfg
# except ModuleNotFoundError:
#     pass
import socket
import json
try:
    from obj.utilites.utility_box import UtilityBox
except ModuleNotFoundError:
    pass

PUBLIC_IP_URL = 'http://jsonip.com'
class IpGetter(object):
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

if __name__ == "__main__":
    print("My public ip is "+str(IpGetter.get_public_ip())+\
        " and my local network ip is "+str(IpGetter.get_local_ip()))
