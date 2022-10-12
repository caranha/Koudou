import os
import time
import datetime
# import pandas as pd

class Logger():
    def __init__(self, exp_name):
        self.exp_name = exp_name
        self.path     = os.path.join("results",exp_name,f"{int(time.time())}")
        self.files    = {}
        self.headers ={}
        os.makedirs(self.path, exist_ok=True)


    def write_data(self, filename, data):
        data = "\n".join([",".join(map(str, e)) for e in zip(*data)])
        self.files[filename].write(data+"\n")

    def write_line(self, filename, data):
        self.files[filename].write(data+"\n")

    def add_file(self, filename, header=None):
        self.files[filename] = open(f"{self.path}/{filename}", "a")

        if header is not None:
            self.files[filename].write(header)

    def write_csv_data(self, filename, data):
        header = self.headers[filename]
        temp = ""
        for x in header:
            if temp != "":
                temp += ","
            temp += f"{data[x]}"
        self.files[filename].write(temp+"\n")

    def add_csv_file(self, filename, header):
        path = os.path.join(self.path,filename)
        self.files[filename] = open(path, "a")
        self.headers[filename] = header.copy()
        temp = ",".join(header) + "\n"
        self.files[filename].write(temp)

    def add_files(self, filename_list, headers_list):
        for filename, header in zip(filename_list, headers_list):
            self.add_file(filename, header+"\n")

    def close_file(self, filename):
        self.files[filename].close()
        self.files.pop(filename)

    def close_files(self):
        for filename in self.files.keys():
            self.files[filename].close()

        self.files.clear()
