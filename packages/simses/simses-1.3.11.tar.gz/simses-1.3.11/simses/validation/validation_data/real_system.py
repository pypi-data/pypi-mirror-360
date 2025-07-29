import numpy as np
import pandas

from simses.commons.config.validation.general import GeneralValidationConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.log import Logger
from simses.analysis.data.abstract_data import Data


class RealSystemData(Data):

    """
    RealData is abstract class for providing time series values from the values of real profiles given in configuration file
    validation.*.ini. It provides many convenient methods to access real data in order to ease calculations in validation.
    """
    TIME_SERIES = 'time series'
    TIME_UNIT = 'Time'
    AC_POWER_DELIVERED = 'power'
    POWER_UNIT = 'unit'

    __log: Logger = Logger(__name__)

    def __init__(self, simulation_config: GeneralSimulationConfig, validation_config: GeneralValidationConfig, data: pandas.DataFrame, data_unit: dict = None):
        super().__init__(simulation_config, data)
        self.__validation_config: GeneralValidationConfig = validation_config
        self.__data_unit = data_unit

    @property
    def id(self) -> str:
        """

         Returns
         -------
         str:
             Data id as string
         """
        return self.__validation_config.system_label

    @property
    def time(self):
        """
           Time series in s

           Returns
           -------

           """
        time_series = self._get_data(RealSystemData.TIME_SERIES)
        time_unit = self.__data_unit[RealSystemData.TIME_UNIT]

        if time_unit == 's':
            time_series_in_s = time_series
        elif time_unit == 'min':
            time_series_in_s = time_series * 60
        elif time_unit == 'h':
            time_series_in_s = time_series * 60 * 60
        else:
            time_series_in_s = None
            RealSystemData.__log.error('Unsupported time unit for the validation data!')

        return time_series_in_s

    @property
    def power(self):
        """
        Series of delivered ac power values in W

        Returns
        -------

        """
        power = self._get_data(RealSystemData.AC_POWER_DELIVERED)
        power_unit = self.__data_unit[RealSystemData.POWER_UNIT]

        if power_unit == 'W':
            power_in_w = power
        elif power_unit == 'kW':
            power_in_w = power * 1e+3
        elif power_unit == 'MW':
            power_in_w  = power * 1e+6
        elif power_unit == 'GW':
            power_in_w = power * 1e+9
        else:
            power_in_w = None
            RealSystemData.__log.error('Unsupported power unit for the validation data!')

        return power_in_w

    @property
    def dc_power(self):
        """
        Series of power values in W

        Returns
        -------

        """
    @property
    def dc_power_storage(self):
        return self._get_data(SystemState.DC_POWER_STORAGE)

    @property
    def energy_difference(self):
        """
        Energy difference of start and end point in kWh

        Returns
        -------

        """

    @property
    def soc(self):
        """
        Series of soc values in p.u.

        Returns
        -------

        """

    @property
    def capacity(self):
        """
        Series of capacity in kWh

        Returns
        -------

        """

    @property
    def state_of_health(self):
        """
        Series of state of health in p.u.

        Returns
        -------

        """

    @property
    def storage_fulfillment(self):
        """
        Percentage of time the system or battery can fulfill the desired power

        Returns
        -------

        """

    @classmethod
    def get_system_data(cls, path: str, config: GeneralSimulationConfig) -> list:
        """
        Extracts unique systems data from storage data files in path

        Parameters
        ----------
        path : value folder
        config : simulation data_config in value folder

        Returns
        -------

        """
        pass
