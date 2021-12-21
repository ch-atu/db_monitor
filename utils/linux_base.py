# encoding : utf-8
import re
import time

import paramiko


class LinuxBase(object):
    def __init__(self,params):
        self.params = params
        self.hostname = self.params['hostname']
        self.port = self.params['port']
        self.username = self.params['username']
        self.password = self.params['password']

    @classmethod
    def convert_params(cls,params):
        params['port'] = int(params.get('port', 0))
        return params

    # ssh connection and sftp connection
    def connection(self):
        self.params = self.convert_params(self.params)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            print('开始连接服务器！')
            ssh_client.connect(**self.params,allow_agent=False)
            t = paramiko.Transport((self.hostname,int(self.port)))
            # t.banner_timeout = 300  # 修复连接中断的问题
            t.connect(username=self.username,password=self.password)
            sftp_client = paramiko.SFTPClient.from_transport(t)
            print('服务器连接成功！')
            return ssh_client,sftp_client
        except Exception as e:
            print("linux连接异常:{}".format(e))
            return None, None
    # read all of file content

    def readfile(self,file,seek=0, tags=None):
        _,sftp_client = self.connection()
        try:
            file_size = sftp_client.stat(file).st_size
            with sftp_client.open(file, 'rb') as remote_file:
                remote_file.prefetch(file_size)
                remote_file.seek(seek)
                while True:
                    line = remote_file.readline()
                    if not line:
                        break
                    yield line, 0

            yield b'', remote_file.tell()
        except Exception as e:
            print("读取文件错误！")
            # from utils.tools import mysql_exec
            # if re.findall('redis', file):
            #     print("删除redis日志路径！")
            #     sql = "update redis_list set log='{}' where tags='{}' ".format('', tags)
            #     mysql_exec(sql)
            #     print("删除成功")
            # if re.findall('mysql', file):
            #     print("删除mysql慢查询日志路径！")
            #     sql = "update mysql_list set slowquery_log='{}' where tags='{}' ".format('',tags)
            #     mysql_exec(sql)
            #     print("删除成功！")
            #     # time.sleep(5)
            return None, None

    # read last n of file content
    def readfile_n(self,file,num):
        cmd = 'tail -{} {}'.format(num,file)
        ssh_client,_ = self.connection()
        std_in, std_out, std_err = ssh_client.exec_command(cmd)
        for line in std_out.read().splitlines():
            if line != '':
                yield (line,0)

    def exec_command(self,command,ssh_client=None):
        try:
            if not ssh_client:
                ssh_client, _ = self.connection()
            std_in, std_out, std_err = ssh_client.exec_command(command)
            return std_out
        except Exception as e:
            print(e)

    def exec_command_res(self,command,ssh_client=None):
        #
        try:
            if not ssh_client:
                ssh_client, _ = self.connection()
            std_in, std_out, std_err = ssh_client.exec_command(command)
            res = std_out.read().decode()
            print('执行命令：{}，执行结果：{}'.format(command,res))
            return res
        except Exception as e:
            print(e)

    def sftp_upload_file(self,local_file,remote_file):
        try:
            _, sftp_client = self.connection()
            sftp_client.put(local_file, remote_file)
        except Exception as e:
            print(e)

    def sftp_down_file(self,remote_file, local_file):
        try:
            _, sftp_client = self.connection()
            sftp_client.get(remote_file, local_file)
        except Exception as e:
            print(e)


# if __name__ == '__main__':
#     linux_params = {
#         'hostname': '119.29.139.149',
#         'port': 22,
#         'username': 'ubuntu',
#         'password': 'ch2020...'
#     }
#     l = LinuxBase(params=linux_params)
#     print(l.readfile(file='/var/log/mysql/error.log', seek=52395))



