"""
Provides capabilities for parsing an input file where comments are ignored and key-value pairs
are separated by spaces
"""
import re
import logging

logger = logging.getLogger(__name__)

class InputFileParser(object):
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
        logger.info('AUTHOR             =  Name of the author of the table (str)')
        logger.info('PREFIX       =  Prefix of the flamelets to be read if there are multiple directories(str)')
        logger.info('FLAMELETTYPE       =  Format of the flamelet files (FlameMaster, Cantera)')
        logger.info('FLAMELETPATHS      =  Folder(s) containing the flamelets (str). Can use wildcards for multiple files e.g. stuff*.txt')
        logger.info('TABLETYPE          =  Output format of the chemical table. (FPVA, FPVT, FPVC) (str)')
        logger.info('CLOSURETYPE        =  Closure method to use for generating the table (Beta, thickenedFlame) (str)')
        logger.info('EOS                =  For FPVC tables, the type of treatment to handle compressible variables. (ideal, pengrobinson) (str)')
        logger.info('REALFLUIDS         =  For FPVC tables, with real fluids, this is a string list of species to be treated as real. (str)')
        logger.info('REALFLUIDDATA      =  For FPVC tables with real fluids, the method for obtaining critical fluid properties.(coolprop, ascii) (str)')
        logger.info('NZMEAN             =  Number of points in mixture fraction space (int)')
        logger.info('NCMEAN             =  Number of points in the progress variable space (int)')
        logger.info('NSMIX              =  Number of points in the mixedness space (int)')
        logger.info('VARIANCE           =  Type of variance to use(SMIX or ZVAR) (str)')
        logger.info('OUTPUTVARIABLES    =  Variables to include in table. Leave blank to produce minimum table output variables')
        logger.info('OUTPUTNAME         =  Name of flamelet table')
        logger.info('BOUNDARYREFINEMENT =  Use the spacing from the flamelet solutions at the boundaries (bool)')
        logger.info('TABLEVERIFICATION  = ')
        logger.info('GENERATEREPORT     = ')

