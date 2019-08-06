import re
import logging

logger = logging.getLogger(__name__)


class InputFileParser(object):
    """
    Provides capabilities for parsing an input file where comments are ignored and key-value pairs
    are separated by spaces
    """
    def __init__(self, file_name):
        self.user_input_data = {}
        self.input_file_name = ''
        self.read_input_file(file_name)

    def read_input_file(self, file_name):
        try:
            with open(file_name):
                pass
        except IOError:
            logger.error('Error: the file ' + file_name + ' could not be found.')

        self.input_file_name = file_name
        with open(file_name) as f:
            for line in f:
                li = line.strip().rstrip()
                li = re.sub(r'\s*#.*', '', li) #Remove comments
                if li:
                    li = li.split(' ', 1)
                    key = li[0].strip()
                    value = li[1].strip()
                    self.user_input_data[key] = value

    @staticmethod
    def print_valid_keywords():
        logger.info('The following keywords can be used in the input file:')


