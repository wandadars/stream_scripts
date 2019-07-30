import logging

logger = logging.getLogger(__name__)

class user_input_parser(object):
    def __init__(self):
        self.file_name = []
        self.file_path = []

    def parse_user_input_file(self,file_path, file_name):
        import sys
        print("Reading Data From: %s"%(file_name))
        try:
            f = open(file_path, "r")
        except:
            print("Failed to Input File!")
            sys.exit(1)


        input_data = {}
        for file_line in f:
            Line = file_line.rstrip()
            if Line.startswith('#') == False:
                if Line != '' :
                    Line = Line.rsplit('#')[0]
                    Line = Line.split('=')
                    input_data[Line[0].strip()] = Line[1].strip()
        f.close()
        return input_data

def compute_filename_numbers(start, stop, step):
    num_files = (stop - start)/step
    file_indicies = []
    iterate = start
    for i in range(0, num_files):   #make list of timestamps
        file_indicies.append(iterate)
        iterate = iterate + step
    return file_indicies


