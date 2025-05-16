import ftplib
import logging as logger
import os

import paramiko
import config.settings as settings
from base64 import decodebytes


class SFTP_Service():
    def __init__(self):
        self.logger = logger.getLogger("main")

    # def send_files_sftp(self):
    #     try:
    #         self.logger.info(f"SFTP send files task")
    #         print("BEGIN SEND")
    #         files_csv = []
    #         file_csv=""
    #         for fname in os.listdir('./files'):
    #             if fname.endswith('.csv') and fname.__len__()>8:
    #                 files_csv.append("./files/"+fname+"")
    #                 self.logger.info(f"SFTP task found file:{fname}")

    #         if len(files_csv) > 0:
    #             print("FILES EXISTS")
    #             host = settings.HOST_SFTP
    #             port = settings.PORT_SFTP
    #             username = settings.USERNAME_SFTP
    #             password= settings.PASSWORD_SFTP
    #             remote_dir = settings.REMOTEDIR_SFTP
                        
    #             self.logger.info(f"SFTP connect to host:{host} port:{port} user:{username} password:{password}")
    #             print("CONNECT FTP")
    #             ftp = ftplib.FTP()
    #             print("INSTANCE")
    #             ftp.connect(host=host, port=port)
    #             print("CONNECT")
    #             ftp.login(user=username, passwd = password)
    #             print("END LOGIN FTP")
    #             if (remote_dir != ""):
    #                 self.logger.info(f"SFTP Changing to directory:{remote_dir}")
    #                 ftp.cwd(remote_dir)

    #             for file_csv in files_csv:
    #                 self.logger.info(f"Sending file to sftp:{file_csv}")
    #                 ftpResponseMessage = ftp.storbinary(f'STOR {os.path.split(file_csv)[1]}', open(file_csv, 'rb'))
    #                 #https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes
    #                 if ("226" in str(ftpResponseMessage)):
    #                     self.logger.info("File sent correctly")
    #                     os.remove(file_csv)
    #     except Exception as ex:
    #         print(f"Exception send:{ex}")
    #         self.logger.error(f"Exception send file to sftp:{ex}")


    def send_files_sftp(self):
        sftp=None
        try:
            
            keydata = settings.KEYS_SSH_RSA_SFTP_SERVERS
            host = settings.HOST_SFTP
            port = settings.PORT_SFTP
            username = settings.USERNAME_SFTP
            password= settings.PASSWORD_SFTP
            files_csv = []
            files_path="./files/"

            for fname in os.listdir(files_path):
                if fname.endswith('.csv') and fname.__len__()>8:
                    files_csv.append(fname)
                    self.logger.info(f"SFTP task found file:{fname}")
            
            if len(files_csv) > 0:
                client = paramiko.SSHClient()
                for key in keydata:
                    client.get_host_keys().add(host, 'ssh-rsa', paramiko.RSAKey(data=decodebytes(key)))
                client.connect(hostname=host,username=username,password=password,port=port,timeout=5)
                sftp=client.open_sftp()
                
                for file_csv in files_csv:
                    sftp.put(files_path+file_csv, "/"+file_csv+"")
                    self.logger.info("File sent correctly")
                    os.remove(files_path+file_csv)
                    
                sftp.close()
                client.close() 
        except Exception as ex:
            self.logger.error(f"Exception send file to sftp:{ex}")
            if sftp!= None:
                sftp.close()
                client.close()