import os
import sys


class user_input_parser(object):
    def __init__(self):
        self.file_name = []
        self.file_path = []

    def parse_user_input_file(self,file_name, file_path):
        print("Reading Data From: %s"%(file_name))
        try:
            f = open(file_path + '/' + file_name, "r")
        except:
            print("Failed to Input File!")
            raise

        input_data = {}
        for file_line in f:
            Line = file_line.rstrip()
            if Line.startswith('#') == False:
                if Line != '' :
                    Line = Line.rsplit('#')[0].strip()
                    Line = Line.split(' ')
                    print(Line)
                    input_data[Line[0].strip()] = Line[-1].strip()
        f.close()
        return input_data



