# This file will generate the load or generation file from given mat
from simses.commons.profile.power.power_file_generator import FileGenerator

class LoadFileGenerator(FileGenerator):

    def __init__(self, input_file):
        super().__init__()
