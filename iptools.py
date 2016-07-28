# coding=utf-8
import os, sys, fnmatch
import socket
import struct
import time

class IP:
    def __init__(self, filename):
        self.base_path = os.getcwd()
        self.filename = self.base_path + '/' + filename
        self.offset = 0
        self.index = ''
        self.fp = ''
        self.fpd = ''

    def init(self):
        if not self.fp:
            self.fp = open(self.filename, "rb")
        if not self.fpd:
            self.fpd = open('./csv/ip.csv','w+',encoding='utf-8')
        self.offset, = struct.unpack('>I', self.fp.read(4))
        if self.offset < 4:
            sys.exit("Invalid %s file!" % self.filename)
        self.index = self.fp.read(self.offset - 4)

    @staticmethod
    def ip2long(sip):
        """
        Convert an IP string to long
        """
        packed = socket.inet_aton(sip)
        return struct.unpack("!L", packed)[0]

    @staticmethod
    def long2ip(lip):
        """
        Convert an long to IP string
        """
        return socket.inet_ntoa(struct.pack('!L', lip))

    def allip(self):
        self.init()
        max_comp_len = self.offset - 1024 - 4
        sign = 8 + 1024
        start_ip_long = 0
        while True:
            if sign < max_comp_len:
                end_ip_long, = struct.unpack('>I', self.index[sign:sign+4])
                index_offest, = struct.unpack('<I',self.index[sign+4:sign+7]+b"\x00")
                index_length =  self.index[sign+7]
                self.fp.seek(self.offset + index_offest - 1024)
                info  = self.fp.read(index_length).decode('utf8').split('\t')
                info.insert(0,self.long2ip(end_ip_long))
                info.insert(0,self.long2ip(start_ip_long))
                self.wirtecsv(','.join(info))
                start_ip_long = end_ip_long + 1
                sign += 8
            else:
                break

    def wirtecsv(self,ipstr):
        self.fpd.write(ipstr + '\n')
        self.fpd.flush()

    def __del__(self):
        if self.fp:
            self.fp.close()
        if self.fpd:
            self.fpd.close()


def iterfindfiles(path, fnexp):
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, fnexp):
            yield os.path.join(root, filename)


def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

if __name__ == "__main__":
    os.chdir(cur_file_dir())
    filename = [filename for filename in iterfindfiles(r".",  "*.dat")]
    if len(filename) == 1:
        if not os.path.exists('csv'):
            os.mkdir("csv")
        ip = IP(filename[0])
        ip.allip()
        print("Success !")
        time.sleep(10)
    else:
        print("Too many bytefiles or not !")
        time.sleep(10)
        sys.exit(1)
