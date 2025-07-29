from requests import Session
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
import json

class Api(object):
    def __init__(self, server_url: str, api_key: str, api_password: str) -> None:
        # Base URL
        self.BASE_URL = server_url

        # Setup session
        self.session = Session()
        self.session.verify = False
        disable_warnings(InsecureRequestWarning)

        # Base params
        # API & authentication params preparation
        self.baseParams = {
            "api": "json",
            "apikey": api_key,
            "apipass": api_password,
            "do": 1
        }

        # Request status
        self.error = False
        self.error_code = ""
        self.error_message = ""


    def __request(self, method: str, paramsDict: dict, dataDict: dict = {}) -> dict:
        """
        Make a request to API
        Specifically for automatic parameters handle.

        :param method: Request method
        :param paramsDict: Required parameters, in dictionary
        """
        params = self.baseParams
        params.update(paramsDict)

        req = self.session.request(method=method, url=self.BASE_URL, params=params, data=dataDict)
        return req.json()


    # Functions: List VM
    def listVM(self):
        """
        List VMs in an account.
        """
        req = self.__request("GET", {
            "act": "listvs"
        })

        return req["vs"]

    # Functions: VM info
    def VMInfo(self, vps_id):
        """
        Get specific VM information.

        :param vps_id: VPS ID number
        """
        req = self.__request("GET", {
            "act": "vpsmanage",
            "svs": int(vps_id)
        })
        
        return req["info"]

    # Functions: Start VM
    def StartVM(self, vps_id):
        """
        Start a specific VM.

        :param vps_id: VPS ID number
        """
        req = self.__request("GET", {
            "act": "start",
            "svs": int(vps_id),
        })
        
        return req

    # Functions: Stop VM
    def stopVM(self, vps_id):
        """
        Stop a specific VM.

        :param vps_id: VPS ID number
        """
        req = self.__request("GET", {
            "act": "stop",
            "svs": int(vps_id),
        })
        
        return req

    # Functions: List OS
    def listOS(self, vps_id):
        """
        List available OSes for a specific VM.

        :param vps_id: VPS ID number
        """
        req = self.__request("GET", {
            "act": "ostemplate",
            "svs": int(vps_id),
        })

        return req["oslist"]["vzo"]

    # Functions: Restart VM
    def restartVM(self, vps_id):
        """
        Restart a specific VM.

        :param vps_id: VPS ID number
        """
        req = self.__request("GET", {
            "act": "restart",
            "svs": int(vps_id),
        })
        
        return req


    # Private functions: Request List VDF
    def __reqListVDF(self, vps_id):
        """
        HTTP Request of List VDFs for a specific VM.

        :param vps_id: VPS ID number
        """
        req = self.__request("GET", {
            "act": "managevdf",
            "svs": int(vps_id),
        })
        
        return req

    # Functions: List VDF
    def listVDF(self, vps_id):
        """
        List VDFs for a specific VM.

        :param vps_id: VPS ID number
        """
        req = self.__reqListVDF(vps_id)

        return req["haproxydata"]

    # Functions: Get VDF additional info
    def getVDFInfo(self, vps_id):
        """
        Get VDF additional info.

        :param vps_id: VPS ID number
        """
        req = self.__reqListVDF(vps_id)

        return {
            "supported_protocols": req["supported_protocols"],
            "src_ips": req["arr_haproxy_src_ips"],
            "dest_ips": list(req["vpses"][list(req["vpses"].keys())[0]]["ips"].keys())
        }

    # Functions: Add VDF
    def addVDF(self, vps_id, protocol, src_port, src_hostname, dest_ip, dest_port):
        """
        Add a VDF for a specific VM.

        :param vps_id: VPS ID number
        :param protocol: Domain Forwarding protocol
        :param src_port: Source port (if using HTTP/HTTPS protocol, use 80/443)
        :param src_hostname: Source domain, if using HTTP/HTTPS protocol
        :param dest_ip: Destination IP
        :param dest_port: Destination port (if using HTTP/HTTPS protocol, use 80/443)
        """
        req = self.__request("POST", paramsDict={
            "act": "managevdf",
        }, dataDict={
            "svs": int(vps_id),
            "vdf_action": "addvdf",
            "protocol": protocol,
            "src_port": src_port,
            "src_hostname": src_hostname,
            "dest_ip": dest_ip,
            "dest_port": dest_port,
        })

        if "error" in req.keys():
            self.error = True
            self.error_code = list(req["error"].keys())[0]
            self.error_message = list(req["error"].values())[0]

            return {
                "error": req["error"],
                "error_code": self.error_code,
                "error_message": self.error_message
            }
        else:
            return req
