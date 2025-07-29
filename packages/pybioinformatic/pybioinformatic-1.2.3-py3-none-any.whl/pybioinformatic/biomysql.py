"""
File: biomysql.py
Description: MySQL python API.
CreateDate: 2024/10/15
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from sshtunnel import SSHTunnelForwarder
from pymysql import connect


class BioMySQL:
    def __init__(self,
                 mysql_host: str,
                 mysql_port: int,
                 mysql_user: str,
                 mysql_password: str,
                 ssh_ip: str = None,
                 ssh_port: int = None,
                 ssh_user: str = None,
                 ssh_password: str = None,
                 remote_bind_ip: str = None,
                 remote_bind_port: int = None,
                 local_bind_ip: str = None,
                 local_bind_port: int = None):
        # MySQL params
        self.mysql_host = mysql_host if not local_bind_ip else local_bind_ip
        self.mysql_port = mysql_port if not local_bind_port else local_bind_port
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        # SSH params
        self.ssh_ip = ssh_ip
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.remote_bind_ip = remote_bind_ip
        self.remote_bind_port = remote_bind_port
        self.local_bind_ip = local_bind_ip
        self.local_bind_port = local_bind_port

    def __enter__(self):
        if self.local_bind_ip:
            self.connect_server_by_ssh()
            self.ssh_server.start()
        return self.connect_mysql()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.mysql_server.cursor().close()
            self.mysql_server.close()
            self.ssh_server.stop()
        except Exception:
            pass

    def connect_server_by_ssh(self):
        self.ssh_server = SSHTunnelForwarder(
            (self.ssh_ip, self.ssh_port),
            ssh_username=self.ssh_user,
            ssh_password=self.ssh_password,
            remote_bind_address=(self.remote_bind_ip, self.remote_bind_port),
            local_bind_address=(self.local_bind_ip, self.local_bind_port)
        )
        return self.ssh_server

    def connect_mysql(self):
        conf = {
            'host': self.mysql_host,
            'port': self.mysql_port,
            'user': self.mysql_user,
            'password': self.mysql_password,
            'charset': 'utf8',
        }
        self.mysql_server = connect(**conf)
        return self.mysql_server
