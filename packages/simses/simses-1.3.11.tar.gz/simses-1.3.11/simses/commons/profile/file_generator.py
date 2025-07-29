# This file will generate the load or generation file from given mat
import os
import numpy as np
import csv
import scipy.io as scio
from configparser import ConfigParser
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.utils.utilities import get_path_for
from abc import ABC, abstractmethod


class FileGenerator(ABC):

    def __init__(self, profile_filename: str, input_filename: str = None, config: ConfigParser = None, config_path: str = None):
        self.__config_profile: ProfileConfig = ProfileConfig(config, config_path)

        self.__file_out: str = self.generate_path_for_file(profile_filename, is_file_in=False)
        self.__file_in: str = self.generate_path_for_file(input_filename, is_file_in=True)

        self.__all_loaded_data: dict = self.__load_input_data()
        self.__header: dict = self.__get_header_from_input(self.__all_loaded_data)
        self.__data: dict = self.__get_data_from_input(self.__all_loaded_data)

    @abstractmethod
    def generate_csv_file(self):
        # time data and power data should be list or ndarray

        f_out = open(self.__file_out, 'w', newline='')
        self.__write_header_to_power_file(f_out, self.__header)
        self.__write_data_to_power_file(f_out, self.__data)
        f_out.close()

    def generate_path_for_file(self, filename: str = None, is_file_in: bool = False):
        if is_file_in:
            file_with_extension = self.__add_extension_to(filename, is_file_in)
            filepath = os.path.join(get_path_for(file_with_extension), file_with_extension)
        else:
            filepath = None
            if filename is not None:
                filepath = self.__add_extension_to(filename, is_file_in)
            else:
                print('No profile file name is specified! Path to the file can not be generated.')

        return filepath

    def __load_input_data(self):
        if self.__file_in.endswith('.mat'):
            mat_file = scio.loadmat(self.__file_in)
            return mat_file
        else:
            raise Exception('Input file format not supported!')

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
                    if os.path.isfile(filename + extension):
                        filename += extension
                        break
            else:
                for extension in cls.SUPPORTED_OUT_EXTENSIONS:
                    filename += extension
                    break

        return filename

    @abstractmethod
    def __get_header_from_input(cls, input_data):

        pass

    @abstractmethod
    def __get_data_from_input(cls, input_data):

        pass

    @abstractmethod
    def __write_header_to_power_file(self, file_open, header: dict):

        pass

    @abstractmethod
    def __write_data_to_power_file(self, file_open, data: dict):

        pass

    @staticmethod
    def convert_list_to_array(data):
        if type(data) == list:
            data_array = np.array(data)
        else:
            data_array = data

        return data_array
