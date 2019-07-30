import sys
import logging

import input_parser as ip
import lagrangian_analyzer as analyzers

logger = logging.getLogger(__name__)

class Main(object):
    def __init__(self, input_file_name):
        self.input_file_name = input_file_name
        self.setup_logger()
    
    def setup_logger(self):
        logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s: %(message)s', datefmt='%m/%d/%Y %H:%M %p', filename='out.log', filemode='w', level=logging.DEBUG)

        #For console output from logging
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def run(self):
        input_parser = ip.InputFileParser(self.input_file_name)
        
        lagrangian_analyzer = None
        if input_parser.user_input_data['mode'].lower() == 'pdf':
            logger.debug('PDF Analyzer selected')
            lagrangian_analyzer = analyzers.LagrangianParticlePDFDataAnalyzer(input_parser)
        elif input_parser.user_input_data['mode'].lower() == 'smd':
            logger.debug('SMD Analyzer selected')
            lagrangian_analyzer = analyzers.LagrangianParticleSMDDataAnalyzer(input_parser)
        else:
            raise KeyError('mode setting needs to be pdf or smd')

        lagrangian_analyzer.process_data()

if __name__ == "__main__":
    program = Main(sys.argv[1])
    program.run()

            

