from urllib3.util import connection
import dns.resolver as resolver
from dns import message, rdatatype
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests_toolbelt.adapters.socket_options import SocketOptionsAdapter
import requests
import ssl
import socket
import requests
import json
import base64

class dns:
    def __init__(self, url):
        self.url = url
        self._orig_create_connection = connection.create_connection
        connection.create_connection = self.patched_create_connection
    def resolve_dns(self, host):
        if len(self.url.split("/"))>=3 and self.url.split("/")[2] == host:
            my_resolver  = resolver.Resolver()
            my_resolver.nameservers = ['1.1.1.1']
            return str(my_resolver.query(host)[0])

        if host.count(".") == 3:
            return host

        headers = {
                'accept': 'application/dns-message',
                'content-type': 'application/dns-message',
                }

        q = message.make_query(host, rdatatype.A)
        response = requests.post(self.url, data=q.to_wire(), headers=headers)
        try:
            return message.from_wire(response.content).answer[0].to_rdataset()[0].to_text()
        except:
            return host

    def patched_create_connection(self, address, *args, **kwargs):
        host, port = address
        hostname = self.resolve_dns(host)
        return self._orig_create_connection((hostname, port), *args, **kwargs)

class TLS1_2_Adapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                maxsize=maxsize,
                block=block,
                ssl_version=ssl.PROTOCOL_TLSv1_2)

class session:
    def __init__(self, bind="", proxy="", force_tls1_2=False):
        self.session = requests.Session()
        if bind != "":
            if "." not in bind:
                options = [(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, bind.encode())]
                bind = ""
            else:
                options = []

            self.session.get_adapter('http://').init_poolmanager(
                    connections=requests.adapters.DEFAULT_POOLSIZE,
                    maxsize=requests.adapters.DEFAULT_POOLSIZE,
                    source_address=(bind, 0),
                    socket_options=options
                    )
            if force_tls1_2:
                self.session.get_adapter('https://').init_poolmanager(
                    connections=requests.adapters.DEFAULT_POOLSIZE,
                    maxsize=requests.adapters.DEFAULT_POOLSIZE,
                    source_address=(bind, 0),
                    socket_options=options,
                    ssl_version = ssl.PROTOCOL_TLSv1_2
                    )
            else:
                self.session.get_adapter('https://').init_poolmanager(
                    connections=requests.adapters.DEFAULT_POOLSIZE,
                    maxsize=requests.adapters.DEFAULT_POOLSIZE,
                    source_address=(bind, 0),
                    socket_options=options
                    )
        else:
            if force_tls1_2:
                self.session.mount('https://', TLS1_2_Adapter())

        if proxy != "":
            self.session.proxies= { "http": proxy, "https": proxy }

    def get_session(self):
        return self.session

def parse_params(params, name, default=""):
    for p in params:
        if p.split("=")[0] == name and len(p.split("=")) >= 2:
            return p[len(p.split("=")[0])+1:]
    return default


