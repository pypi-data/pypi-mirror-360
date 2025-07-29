import numpy as np
import scipy.interpolate
from scipy.interpolate import RegularGridInterpolator

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.commons.utils.cell_reader import IseaCellReader
from simses.technology.lithium_ion.cell.format.round_18650 import RoundCell18650
from simses.technology.lithium_ion.cell.thermal.default import DefaultThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class IseaCellType(CellType):

    # TODO
    # 1) Make cell type only depend on values from cell reader, no hardcoded values anymore
    # -done- 2) How to handle multiple input files? How to instantiate multiple cell types?
    #   a) One distinct cell type for each file --- drawback: very inconvenient for > 100 cell files
    #   b) Instantiate all cell types in one directory --- how to make this configurable?
    # -> c) file name handed over in constructor of cell type --- batch processing sets files, config could be tricky
    # 3) Documentation is missing
    # 4) Tests are missing

    __EXTENSION: str = '.xml'

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig, file_name: str):
        self.__name: str = type(self).__name__ + ' with ' + file_name
        cell: IseaCellReader = IseaCellReader(battery_data_config.isea_cell_dir + file_name + self.__EXTENSION)
        isea_cell_properties = cell.get_cell_properties()
        super().__init__(voltage, capacity, soh, isea_cell_properties, DefaultThermalCellProperties(),
                         RoundCell18650(), battery_config)

        ocv_mat: np.ndarray = cell.get_open_cicuit_voltage()
        ocv_soc_arr: np.ndarray = cell.get_open_cicuit_voltage_soc()
        ocv_temp_arr: np.ndarray = cell.get_open_cicuit_voltage_temperature()

        if len(ocv_temp_arr.T) == 1:
            self.__open_circuit_voltage_interpolation = scipy.interpolate.interp1d(ocv_soc_arr, ocv_mat,kind='linear')
            self.__temperature_dependency = False
        else:
            self.__temperature_dependency = True
            self.__open_circuit_voltage_interpolation = RegularGridInterpolator((ocv_temp_arr, ocv_soc_arr), ocv_mat)
        rint_mat: np.ndarray = cell.get_internal_resistance()
        rint_soc_arr: np.ndarray = cell.get_internal_resistance_soc()
        rint_temp_arr: np.ndarray = cell.get_internal_resistance_temperature()
        if len(ocv_temp_arr.T) == 1:
            self.__internal_resistance_interpolation = scipy.interpolate.interp1d(rint_soc_arr, rint_mat,kind='linear')
        else:
            self.__internal_resistance_interpolation = RegularGridInterpolator((rint_temp_arr, rint_soc_arr),rint_mat)

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        soc: float = battery_state.soc * 100.0
        temp: float = battery_state.temperature - 273.15
        if self.__temperature_dependency:
            res: float = float(self.__open_circuit_voltage_interpolation((temp, soc)))
        else:
            res: float = float(self.__open_circuit_voltage_interpolation(soc))

        # print(soc, temp, res)
        return res * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        soc: float = battery_state.soc * 100.0
        temp: float = battery_state.temperature - 273.15
        if self.__temperature_dependency:
            res: float = float(self.__internal_resistance_interpolation((temp, soc)))
        else:
            res: float = float(self.__internal_resistance_interpolation(soc))
        # print(soc, temp, res)
        return res / self.get_parallel_scale() * self.get_serial_scale()

    def get_name(self) -> str:
        return self.__name

    def close(self):
        pass
