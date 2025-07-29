# This file will generate the load or generation file from given mat
import os
import numpy as np
import csv
import scipy.io as scio
from configparser import ConfigParser
#from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.utils.utilities import get_path_for


class PowerFileGenerator:

    EXT_IN_MAT: str = '.mat'
    SUPPORTED_IN_EXTENSIONS: [str] = list()
    SUPPORTED_IN_EXTENSIONS.append(EXT_IN_MAT)

    EXT_OUT_CSV: str = '.csv'
    SUPPORTED_OUT_EXTENSIONS: [str] = list()
    SUPPORTED_OUT_EXTENSIONS.append(EXT_OUT_CSV)

    HEADER_DEFAULT = {'Time': 's', 'Unit': 'W', 'Sampling in s': 1, 'Timezone': 'UTC'}
    HEADER_DELIMITER = ':'

    DATA_NAME = ['time series', 'power']
    DATA_DELIMITER = ','

    TIME_SERIES = 'time series'
    POWER = 'power'

    def __init__(self, profile_filename: str, input_filename: str = None):
        #self.__config_profile: ProfileConfig = ProfileConfig(config, config_path)
        self.__profile_filename = profile_filename
        self.__file_out: str = self.generate_path_for_file(profile_filename, is_file_in=False)
        self.__file_in: str = self.generate_path_for_file(input_filename, is_file_in=True)

        self.__all_loaded_data: dict = self.__load_input_data()
        self.__header: dict = self.__get_header_from_input(self.__all_loaded_data)
        self.__data: dict = self.__get_data_from_input(self.__all_loaded_data)

    def generate_csv_file(self):
        # time data and power data should be list or ndarray
        if self.__file_out is not None:
            if self.__header is not None and self.__data is not None:
                f_out = open(self.__file_out, 'w', newline='')
                self.__write_header_to_power_file(f_out, self.__header)
                self.__write_data_to_power_file(f_out, self.__data)
                f_out.close()
            else:
                print(self.__profile_filename + ' can not be generated,because the header or data are not extracted from the given file correctly. ')
        else:
            print(self.__profile_filename + ' can not be generated, because the aim directory of the profile file is incorrect.')

    def generate_path_for_file(self, filename: str = None, is_file_in: bool = False):
        if filename is not None:
            if is_file_in:
                try:
                    file_with_extension = self.__add_extension_to(filename, is_file_in)
                    filepath = os.path.join(get_path_for(file_with_extension), file_with_extension)
                except FileNotFoundError as err:
                    filepath = None

            else:
                if filename is not None:
                    filepath = self.__add_extension_to(filename, is_file_in)
                else:
                    filepath = None
                    print('No profile file name is specified! Path to the file can not be generated')

            return filepath
        else:
            return None

    def __load_input_data(self):
        if self.__file_in is not None:
            if self.__file_in.endswith('.mat'):
                mat_file = scio.loadmat(self.__file_in)
                return mat_file
            else:
                raise Exception('Input file format not supported!')
        else:
            return None

    @classmethod
    def __has_extension(cls, filename: str, is_file_in: bool) -> bool:
        has_extension: bool = False
        if is_file_in:
            for extension in cls.SUPPORTED_IN_EXTENSIONS:
                has_extension |= filename.endswith(extension)
        else:
            for extension in cls.SUPPORTED_OUT_EXTENSIONS:
                has_extension |= filename.endswith(extension)

        return has_extension

    @classmethod
    def __add_extension_to(cls, filename: str, is_file_in: bool) -> str:
        has_extension: bool = cls.__has_extension(filename, is_file_in)
        if not has_extension:
            if is_file_in:
                for extension in cls.SUPPORTED_IN_EXTENSIONS:
                    #if os.path.isfile(filename + extension):
                    filename += extension
                    break
            else:
                for extension in cls.SUPPORTED_OUT_EXTENSIONS:
                    filename += extension
                    break

        return filename

    @classmethod
    def __get_header_from_input(cls, input_data):
        if input_data is not None:
            header: dict = dict()
            var = input_data.keys()
            for name, default_value in cls.HEADER_DEFAULT.items():
                name_rep = name.replace(' ', '_')
                if name_rep in var:
                    header[name] = input_data[name_rep].item()
                else:
                    header[name] = default_value

            return header
        else:
            return None

    @classmethod
    def __get_data_from_input(cls, input_data):
        if input_data is not None:
            data: dict = dict()
            var = input_data.keys()
            for name in cls.DATA_NAME:
                name_rep = name.replace(' ', '_')
                if name_rep in var:
                    data[name] = input_data[name_rep]
                else:
                    raise Exception(name.capitalize() + ' data from input file not found. Writing power profile aborted.')

            return data
        else:
            return None

    def __write_header_to_power_file(self, file_open, header: dict):
        header_writer = csv.writer(file_open, delimiter=self.HEADER_DELIMITER)
        header_writer.writerow(['"""'])

        for key, value in header.items():
            header_writer.writerow(['# ' + key.replace('_', ' '), value])

        header_writer.writerow(['"""'])

    def __write_data_to_power_file(self, file_open, data: dict):
        # time data and power data should be list or ndarray
        data_writer = csv.writer(file_open, delimiter=self.DATA_DELIMITER)
        time_ndarray = None
        power_ndarray = None

        for name, value in data.items():
            if name == PowerFileGenerator.TIME_SERIES:
                time_ndarray = self.convert_list_to_array(value)
            elif name == PowerFileGenerator.POWER:
                power_ndarray = self.convert_list_to_array(value)

        if time_ndarray is None:
            raise Exception('Time data in the input file not found. Writing power profile aborted.')

        if power_ndarray is None:
            raise Exception('Power data in the input file not found. Writing power profile aborted.')

        if time_ndarray is not None and power_ndarray is not None:
            if time_ndarray.size == power_ndarray.size:
                for idx in range(time_ndarray.size):
                    data_writer.writerow([time_ndarray.item(idx), power_ndarray.item(idx)])

            else:
                raise Exception('The dimension of input time and power data is not the same. Writing power profile aborted.')

    @staticmethod
    def convert_list_to_array(data):
        if type(data) == list:
            data_array = np.array(data)
        else:
            data_array = data

        return data_array

'''
if __name__ == '__main__':
    input_file_name = 'ISEA_household_Day165_PV_1s.mat'

    file_generator: PowerFileGenerator = PowerFileGenerator('generation', input_file_name)
'''