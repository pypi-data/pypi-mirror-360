from copy import deepcopy
import random
import time
import logging
from TDhelper.network.http.REST_HTTP import GET
from threading import Thread

class HostManager:
    def __init__(self) -> None:
        self.__host_cnf_backup__ = {}
        self.__host_cnf__ = {}
        self.__host__ = []
        self.__host_len__ = 0
        self.__monitor_speed__= 10
        
        # self.__health_sniffer__ = ""
        self.__monitor_state__= True
    def __backup_host__(self):
        self.__host_cnf_backup__ = deepcopy(self.__host_cnf__)

    def get_per_http_host(self):
        try:
            return self.__generateHost__(self.getHost())
        except Exception as e:
            raise e

    def getHost(self,exclude:list=[]):
        """getHost
            get an access host cnf.
        Parameters:
            self - <class: HostManager>, hostManager instance.
        Returns:
            success - <class, json>, host cnf json.
            fail - None.
        Raises:
            None
        """
        result = None
        retry = 3
        while (True and retry > 0):
            v = 0 if self.__host_len__ == 1 else random.randint(
                0, self.__host_len__-1)
            if exclude:
                if exclude.__contains__(v):
                    continue
            result = self.__host_cnf__[self.__host__[v]]
            result["serverId"] = self.__host__[v]
            if result['status']:
                break
            retry -= 1
        return result

    def del_host(self,k):
        pass
    
    def get_host_by_key(self, key):
        return self.__host_cnf__[key]

    def register(self, serverId, host, port: int = 80, sniffer="/api/sniffer", proto: str = "http://", status=True):
        """register
            register an rpc host
        Parameters:
            self - <class: HostManager>, hostManager instance.
            serverId - <class: int>, serverId
            host - <class: str>, ip or domain
            port - <class: int>, port. default 80
            sniffer - <class: str>, the healthy sniffer uri. default /api/sniffer
            proto - <class: str>, http:// or https://. default http://
            status - <class: bool>, default True
        Returns:
            None
        Raises:
            10000 - key already exists.
        """
        serverId = str(serverId)
        proto = self.__checken_proto__(proto)
        sniffer= sniffer if sniffer else "/api/sniffer"
        if serverId not in self.__host_cnf__:
            self.__host_cnf__[serverId] = {
                "proto": proto,
                "host": host,
                "port": port,
                "status": status,
                "sniffer": sniffer
            }
            if serverId not in self.__host_cnf_backup__:
                self.__host_cnf_backup__ = {
                    "proto": proto,
                    "host": host,
                    "port": port,
                    "status": status,
                    "sniffer": sniffer
                }
            self.__host__.append(serverId)
            self.__host_len__ = len(self.__host__)
        else:
            raise (Exception("10000, '%s' already exists." % serverId))

    def __checken_proto__(self, v):
        v = v.replace(":", "")
        v = v.replace("/", "")
        v = v+"://"
        return v

    def reload(self):
        '''reload
            reload host conf by host conf backup.
        '''
        self.__host_cnf__ = {}
        self.__host__ = []
        self.__host_len__ = 0
        # self.__health_sniffer__ = ""
        for k, v in self.__host_cnf_backup__.items():
            self.register(k, v["host"], v["port"],
                          v["sniffer"], v["proto"], v["status"])

    def delete(self, serverId):
        """delete
            delete a host cnf.
        Parameters:
            self - <class, HostManager>, hostmanager instance.
            serverId - <class, int|str>, serverId.
        Returns:
            success - serverId
            fail - None
        Raises:
            None.
        """
        if str(serverId) in self.__host_cnf__:
            m_result = self.__host_cnf__.pop(serverId)
            self.__host__.remove(serverId)
            self.__host_len__ = len(self.__host__)
            return m_result
        else:
            return None

    def health(self):
        """health
            check host health status.
        Parameters:
            self - <class, HostManager>, hostmanager instance.
        Returns:
            <class, json>, cheked result.
            json desc
                statistics - <class, json>, checked result.
                    total - host count.
                    health - checked it's success count.
                    unhealthy - checked it's fail count.
                health - <class, list>, health serverId list.
                unhealthy - <class, list>, unhealthy serverId list.
        Raises:
            None.
        """
        while self.__monitor_state__:
            result = {
                "statistics": {
                    "total": self.__host_len__,
                    "health": 0,
                    "unhealthy": 0,
                },
                "health": [],
                "unhealthy": []
            }
            for k in self.__host__:
                m_uri = self.__generateHost__(self.__host_cnf__[k])
                if m_uri:
                    m_uri += "/" + \
                        self.__host_cnf__[k]["sniffer"].strip(
                            '/').replace('\\', "/")
                    status, body = GET(m_uri, time_out=5)
                    if status == 200:
                        self.__host_cnf__[k]['status'] = True
                        logging.info("%s%s:%s%s  success."%(self.__host_cnf__[k]['proto'],self.__host_cnf__[k]['host'],self.__host_cnf__[k]['port'],self.__host_cnf__[k]['sniffer']))
                        result["health"].append(k)
                    else:
                        self.__host_cnf__[k]["status"] = False
                        logging.info("%s%s:%s%s fail."%(self.__host_cnf__[k]['proto'],self.__host_cnf__[k]['host'],self.__host_cnf__[k]['port'],self.__host_cnf__[k]['sniffer']))
                        result["unhealthy"].append(k)
                else:
                    self.__host_cnf__[k]["status"] = False
                    logging.info("%s%s:%s%s fail."%(self.__host_cnf__[k]['proto'],self.__host_cnf__[k]['host'],self.__host_cnf__[k]['port'],self.__host_cnf__[k]['sniffer']))
                    result['unhealthy'].append(k)
            for k in result["unhealthy"]:
                self.delete(k)
            result["statistics"]["health"] = len(result["health"])
            result["statistics"]["unhealthy"] = len(result["unhealthy"])
            time.sleep(self.__monitor_speed__)

    def __start_state_monitor__(self, speed= None):
        self.__monitor_state__= True
        self.__monitor_speed__= speed if speed else self.__monitor_speed__
        monitor= Thread(target= self.health)
        monitor.start()
        
    def __stop_state_monitor__(self):
        self.__monitor_state__= False
        self.__monitor_speed__= 10
        
    def __generateHost__(self, uri_cnf: dict):
        proto = uri_cnf["proto"]
        host = uri_cnf["host"]
        port = str(uri_cnf["port"])
        if uri_cnf["status"]:
            if port != 80 or port != "80":
                return proto+host+":"+port
            else:
                return proto+host
        else:
            return None
