import threading
import re
from TDhelper.network.socket import base,SOCKET_TYPE,SOCKET_EVENT, Event,trigger,call, get_host_ip
from TDhelper.network.socket.protocol.base import Protocol,ANALYSIS_STATUS, analysis
import socket


class Client(base,threading.Thread):
    def __init__(self,ip,port,buffSize=1024,maxReconnect=5,proto:Protocol= None):
        threading.Thread.__init__(self)
        super(Client,self).__init__()
        if re.match(r"^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$", ip, re.I | re.M):
            ip= socket.gethostbyname(ip)
        self._max_reconnect= maxReconnect
        self._reconnect=0
        self.uri=(ip,port)
        self.__proto= proto
        self.__runing=threading.Event()
        self._buffSize=buffSize
        self.__state=True
        self.createsocket(SOCKET_TYPE.TCPIP)
        self.setTimeout(10)
        self.__runing.set()

    def run(self):
        self.__connection()

    @trigger("connection")
    def __connection(self):
        try:
            self.__state= True
            self.connection(self.uri)
            self._reconnect= 0
            recv_thred= threading.Thread(target=self.recvMsg)
            self.on(SOCKET_EVENT.onConnection,self)
            recv_thred.setDaemon(True)
            recv_thred.start()
        except Exception as e:
            self.__state=False
            if self._reconnect>self._max_reconnect:
                self.on(SOCKET_EVENT.onError,e)
            else:
                self._reconnect+=1
                self.__connection()

    @trigger("send")
    def sendMsg(self,buff):
        try:
            if self.__state:
                self.send(self.getSocket(),buff)
        except Exception as e:
            self.on(SOCKET_EVENT.onError,e)

    @trigger("recv")
    def recvMsg(self):
        try:
            m_protocol = None
            m_count= 0
            buff= b''
            conn= None
            if self.__proto:
                m_protocol= analysis(Protocol())
                m_count=0
            while self.__runing.is_set() and self.__state:      
                buff,conn=self.recv(self.getSocket(),self._buffSize)
                if not self.__proto:
                    if not buff:
                        self.__runing.clear()
                        break
                    self.on(SOCKET_EVENT.onRecv,buff)
                else:
                    if not buff:
                        # if client socket is closed set flag is flase,and close connection
                        self.__runing.clear()
                        break
                    '''
                    Recv Event
                    '''
                    m_count+=1
                    #print(buff)
                    m_protocol.recv(buff)
                    if m_protocol.state== ANALYSIS_STATUS.RECV_COMPLETE:
                        self.on(SOCKET_EVENT.onRecv.value, m_protocol, conn)
                        m_protocol.resetState()
            return m_protocol if self.__proto else (buff,conn)
        except Exception as e:
            self.on(SOCKET_EVENT.onError,e)
        finally:
            pass #self.closeClient()

    def setRuning(self):
        if self.__runing.is_set():
            self.__runing.clear()

    def closeClient(self):
        try:
            if self.__state:
                self.__state=False
                self.setRuning()
                self.close()
                #super(Client,self).close()
        except Exception as e:
            self.on(SOCKET_EVENT.onError,e)