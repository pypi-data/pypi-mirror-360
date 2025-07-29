from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.power_electronics.dcdc_converter.abstract_dcdc_converter import DcDcConverter
from simses.commons.utils.utilities import format_float
from simses.commons.log import Logger


class NoLossDcDcConverter(DcDcConverter):

    __volumetric_power_density = 143 * 10 ** 6  # W / m3
    __GRAVIMETRIC_POWER_DENSITY = 11000  # W/kg
    __SPECIFIC_SURFACE_AREA = 0.0001  # in m2 / W  # TODO add exact values

    # Exemplary value from:
    # (https://www.iisb.fraunhofer.de/en/research_areas/vehicle_electronics/dcdc_converters/High_Power_Density.html)

    def __init__(self, max_power: float, intermediate_circuit_voltage: float):
        super().__init__(intermediate_circuit_voltage)
        self.__log: Logger = Logger(type(self).__name__)
        # TODO check validity of code block for limiting DC power
        if max_power == 0.0:
            self.__log.info('Setting ' + type(self).__name__ + ' to maximum reference power of ' + str(self.max_power) + ' W')
            max_power = self.max_power
        self.__max_power: float = max_power
        self.__dc_power_loss: float = 0
        self.__dc_power: float = 0
        self.__dc_current: float = 0

    def calculate_dc_current(self, dc_power: float, storage_voltage: float) -> None:
        dc_power = self.__check_for_max_power(dc_power)
        #self.__dc_power = dc_power
        self.__dc_current = dc_power / storage_voltage

    def reverse_calculate_dc_current(self, dc_power: float, storage_voltage: float) -> None:
        self.__dc_power = dc_power
        self.__dc_current = dc_power / self.intermediate_circuit_voltage

    @property
    def max_power(self) -> float:
        return 1e12

    def __check_for_max_power(self, power: float) -> float:
        if abs(power) > self.__max_power:
            self.__log.info(format_float(power) + ' W is above maximum power for ' + type(self).__name__ + ' of ' +
                            format_float(self.__max_power) + '. Reducing power to maximum power.')
            if self._is_charge(power):
                power = self.__max_power
            else:
                power = -self.__max_power
        return power

    @property
    def dc_power_loss(self):
        return self.__dc_power_loss

    @property
    def dc_power(self):
        return self.__dc_power

    @property
    def volume(self) -> float:
        # return self.max_power / self.__volumetric_power_density
        return 0

    @property
    def mass(self):
        return 0

    @property
    def surface_area(self) -> float:
        return 0

    @property
    def dc_current(self):
        return self.__dc_current

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def close(self) -> None:
        pass
