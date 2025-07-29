import os
import pandas
import numpy as np
import scipy.io as scio
from simses.commons.config.validation.validation_profile import ValidationProfileConfig


class LoadRealData:

    SUPPORTED_IN_EXTENSIONS: str = ['.mat']
    DATA_NAME = ['time series', 'power']
    DATA_UNIT = {'Time': 's', 'unit': 'W', 'Sampling in s': 1}

    TIME = 'time series'
    AC_POWER_DELIVERED = 'ac power delivered'
    DC_POWER_STORAGE = 'dc power storage'
    DC_POWER_INTERMEDIATE = 'dc power intermediate'

    def __init__(self, profile_config: ValidationProfileConfig):
        self.__profile_config: ValidationProfileConfig = profile_config
        self.__ac_power_filename = self.__profile_config.real_ac_power_delivered_profile
        self.__dc_power_storage_filename = self.__profile_config.real_dc_power_storage_profile
        self.__dc_power_intermediate_filename = self.__profile_config.real_dc_power_intermediate_profile
        self.__ac_power_file = None
        self.__dc_power_storage_file = None
        self.__dc_power_intermediate_file = None
        self.__data: dict = {}
        self.__unit: dict = {}
        self.load()

    @property
    def data(self):
        return pandas.DataFrame(self.__data)

    @property
    def unit(self):
        return self.__unit

    def load(self):
        self.__load_all_files()
        self.__load_data()
        self.__load_unit()

    def __load_all_files(self):
        self.__ac_power_file = self.__load_file(self.__ac_power_filename)
        self.__dc_power_storage_file = self.__load_file(self.__dc_power_storage_filename)
        self.__dc_power_intermediate_file = self.__load_file(self.__dc_power_intermediate_filename)

    def __load_data(self):
        data_list: list = []
        ac_power_data = self.__extract_data_array(self.__ac_power_file, LoadRealData.AC_POWER_DELIVERED)
        data_list.append(ac_power_data)

        dc_power_storage_data = self.__extract_data_array(self.__dc_power_storage_file, LoadRealData.DC_POWER_STORAGE)
        data_list.append(dc_power_storage_data)

        dc_power_intermediate_data = self.__extract_data_array(self.__dc_power_intermediate_file, LoadRealData.DC_POWER_INTERMEDIATE)
        data_list.append(dc_power_intermediate_data)

        if LoadRealData.check_data_dim_consistency(data_list):
            for data in data_list:
                self.__append_data(data)
        else:
            raise Exception('Validation Data are inconsistent in dimension! Please check.')

    def __load_unit(self):
        unit_list: list = []
        ac_power_unit = self.__extract_unit(self.__ac_power_file)
        unit_list.append(ac_power_unit)

        dc_power_storage_unit = self.__extract_unit(self.__dc_power_storage_file)
        unit_list.append(dc_power_storage_unit)

        dc_power_intermediate_unit = self.__extract_unit(self.__dc_power_intermediate_file)
        unit_list.append(dc_power_intermediate_unit)

        if LoadRealData.check_data_unit_consistency(unit_list):
            for unit in unit_list:
                self.__append_unit(unit)
        else:
            raise Exception('Validation Data are inconsistent in unit! Please check.')

    def __load_file(self, filename: str):
        if filename is not None:
            file_with_extension = self.__add_extension_to(filename)
            if file_with_extension.endswith('.mat'):
                mat_file = scio.loadmat(filename)
                return mat_file
            else:
                raise Exception('Input file format not supported!')

        else:
            return None

    def __append_data(self, data_dict: dict):
        if data_dict is not None:
            for key, value in data_dict.items():
                if key not in self.__data.keys():
                    self.__data[key] = value

    def __append_unit(self, unit_dict: dict):
        if unit_dict is not None:
            for key, value in unit_dict.items():
                if key not in self.__unit.keys():
                    self.__unit[key] = value

    def __extract_data_array(self, loaded_file: dict, power_name: str):
        if loaded_file is not None:
            data_dict: dict = {}
            var = loaded_file.keys()
            for name in self.DATA_NAME:
                name_rep = name.replace(' ', '_')
                if name_rep in var:
                    raw_data = loaded_file[name_rep]
                    if name == 'power':
                        data_dict[power_name] = np.reshape(raw_data, raw_data.size)
                    else:
                        data_dict[name] = np.reshape(raw_data, raw_data.size)
                else:
                    raise Exception(
                        name.capitalize() + ' data from input file of ' + power_name + ' not found. Validation regarding these data ignored.')
            return data_dict
        else:
            return None

    def __extract_unit(self, loaded_file: dict):
        if loaded_file is not None:
            unit: dict = dict()
            var = loaded_file.keys()
            for name, value in self.DATA_UNIT.items():
                name_rep = name.replace(' ', '_')
                if name_rep in var:
                    unit[name] = loaded_file[name_rep].item()
                else:
                    unit[name] = value
            return unit

        else:
            return None

    @staticmethod
    def check_data_dim_consistency(data_list: [dict]):
        dim_to_be = 0
        for data_dict in data_list:
            for value in data_dict.values():
                dim = value.size
                if dim_to_be != 0 and dim != dim_to_be:
                    return False
                dim_to_be = dim

        return True

    @staticmethod
    def check_data_unit_consistency(unit_list: [dict]):
        for unit in LoadRealData.DATA_UNIT.keys():
            unit_to_be = 0
            for unit_dict in unit_list:
                value = unit_dict[unit]
                if unit_to_be != 0 and value != unit_to_be:
                    return False
                unit_to_be = value

        return True

    @classmethod
    def __has_extension(cls, filename: str) -> bool:
        has_extension: bool = False
        for extension in cls.SUPPORTED_IN_EXTENSIONS:
            has_extension |= filename.endswith(extension)

        return has_extension

    @classmethod
    def __add_extension_to(cls, filename: str) -> str:
        has_extension: bool = cls.__has_extension(filename)
        if not has_extension:
            for extension in cls.SUPPORTED_IN_EXTENSIONS:
                if os.path.isfile(filename + extension):
                    filename += extension
                    break
        return filename


