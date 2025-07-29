import numpy as np
import pandas

from simses.commons.utils.utilities import format_float


class Description:

    class Technical:
        DELTA_AC_DELIVERED: str = 'Delta delivered AC power'
        DELTA_DC_STORAGE: str = 'Delta DC power storage'
        DELTA_SOC: str = 'Delta SOC'
        SN_DELTA_AC_DELIVERED: str = 'Standard Norm of Delta delivered AC power'
        SN_DELTA_SOC: str = 'Standard Norm of Delta SOC'
        DELTA_MAX_AC_DELIVERED: str = 'Delta max. delivered AC power'
        DELTA_MIN_AC_DELIVERED: str = 'Delta min. delivered AC power'

        DELTA_MEAN_SOC: str = 'Delta SOC mean'
        DELTA_MAX_SOC: str = 'Delta SOC max'
        DELTA_MIN_SOC: str = 'Delta SOC min'

        DELTA_ROUND_TRIP_EFFICIENCY: str = 'Delta Efficiency round trip'
        DELTA_COULOMB_EFFICIENCY: str = 'Delta Coulombic efficiency'

        DELTA_NUMBER_CHANGES_SIGNS: str = 'Delta number of changes of signs per day'
        DELTA_RESTING_TIME_AVG: str = 'Delta avg. length of resting times'
        DELTA_ENERGY_CHANGES_SIGN: str = 'Delta pos. energy between changes of sign'
        DELTA_FULFILLMENT_AVG: str = 'Delta avg. Fulfillment Factor'
        DELTA_EQUIVALENT_FULL_CYCLES: str = 'Delta equivalent full cycles'
        DELTA_DEPTH_OF_DISCHARGE: str = 'Delta avg. depth of cycle for discharge'
        DELTA_REMAINING_CAPACITY: str = 'Delta remaining capacity'
        DELTA_SELF_CONSUMPTION_RATE: str = 'Delta self-consumption rate'
        DELTA_SELF_SUFFICIENCY: str = 'Delta self-sufficiency'
        DELTA_ENERGY_THROUGHPUT: str = 'Delta energy throughput'

        DELTA_MAX_GRID_POWER: str = 'Delta max. grid power'
        DELTA_POWER_ABOVE_PEAK_MAX: str = 'Delta max. grid power above peak'
        DELTA_POWER_ABOVE_PEAK_AVG: str = 'Delta avg. power above peak'
        DELTA_ENERGY_ABOVE_PEAK_MAX: str = 'Delta max. energy event above peak'
        DELTA_ENERGY_ABOVE_PEAK_AVG: str = 'Delta avg. energy event above peak'
        DELTA_NUMBER_ENERGY_EVENTS: str = 'Delta number of energy events above peak'

        DELTA_SOH: str = 'Delta State of Health'


class Unit:
    NONE: str = ''
    PERCENTAGE: str = '%'
    MINUTES: str = 'min'

    WATT: str = 'W'
    KILOWATT: str = 'kW'

    KWH: str = 'kWh'

    KG: str = 'kg'
    EURO: str = 'EUR'


class ComparisonResult:
    """Provides a structure for evaluation results in order to organize data management for printing to
    the console, exporting to csv files, etc.."""

    def __init__(self, description: str, unit: str, value):
        self.__description: str = description
        self.__unit: str = unit
        self.__value = value

    @property
    def description(self) -> str:
        """Description of the result"""
        return self.__description

    @property
    def unit(self) -> str:
        """Unit of the result"""
        return self.__unit

    @property
    def value(self):
        """Value of the result"""
        if isinstance(self.__value, (int, float, complex)) and not np.isnan(self.__value):
            return eval(format_float(self.__value, decimals=2))
        elif isinstance(self.__value, (list, np.ndarray)):
            return [round(value, 2) for value in self.__value]
        elif isinstance(self.__value, dict):
            value_dict = dict()
            for key, data in self.__value.items():
                if isinstance(data, (int, float, complex)) and not np.isnan(data):
                    value_dict[key] = eval(format_float(data, decimals=2))
                elif isinstance(data, (list, np.ndarray)):
                    value_dict[key] = [round(i, 6) for i in data]
                else:
                    value_dict[key] = data

            return value_dict
        else:
            return self.__value

    def to_csv(self) -> pandas.DataFrame:
        """Returns ComparisonResult as a list of strings."""
        res = dict()
        if isinstance(self.__value, dict):
            for key in self.__value.keys():
                label = ' '.join([self.__value[key], self.description]) + ' in ' + self.unit
                res[label] = self.value[key]
        else:
            label = self.description + ' in ' + self.unit
            res[label] = self.value
        return pandas.DataFrame(res)

    @classmethod
    def get_header(cls) -> [str]:
        """Returns the header of ComparisonResult as a list of strings."""
        return [str(Description.__name__), 'Value', str(Unit.__name__)]

    def __str__(self):
        return self.to_csv()

    def __repr__(self):
        return self.to_csv()
