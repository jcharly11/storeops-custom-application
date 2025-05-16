
import ftplib
import os
import unittest


class Test_send_file_sftp(unittest.TestCase):
    
    def test_send_file(self):
        FTP_HOST = "sftp2.smart-control.it"
        FTP_USER = "wirama_test"
        FTP_PASS = "Kcwdx2Kcwdx2"

        session = ftplib.FTP(FTP_HOST,FTP_USER,FTP_PASS)
        file = open('TestJC.csv','rb')                  # file to send
        session.storbinary('1TestJC.csv', file)     # send the file
        file.close()                                    # close file and FTP
        session.quit()

        self.assertTrue(True)
