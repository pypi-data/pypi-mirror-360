import warnings
import numpy
from simses.system.storage_system_dc import StorageSystemDC
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.system import SystemState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel
from simses.system.thermal.ambient.location_temperature import LocationAmbientTemperature
from simses.system.thermal.ambient.user_battery_temperature import UserBatteryTemperatureProfile
from simses.system.thermal.model.system_thermal_model import SystemThermalModel
from simses.technology.storage import StorageTechnology


class NoSystemThermalModel(SystemThermalModel):
    """This model does nothing - keeps the system air temperature equal to ambient temperature"""

    LARGE_NUMBER = numpy.finfo(numpy.float64).max * 1e-100

    def __init__(self, ambient_thermal_model: AmbientThermalModel, general_config: GeneralSimulationConfig,
                 dc_systems: [StorageSystemDC]):
        super().__init__()
        self.__ambient_thermal_model = ambient_thermal_model
        if isinstance(self.__ambient_thermal_model, UserBatteryTemperatureProfile):
            self.__dc_systems: [StorageSystemDC] = dc_systems
            self.__storage_technologies: [StorageTechnology] = list()
            for dc_system in self.__dc_systems:  # Unpack storage technologies and DC/DC converters from StorageSystemDC
                self.__storage_technologies.append(dc_system.get_storage_technology())

        self.start_time = general_config.start
        if isinstance(ambient_thermal_model, LocationAmbientTemperature):
            warnings.warn('LocationAmbientTemperature is chosen with NoSystemThermalModel.\n'
                  'StorageTechnology temperatures will be initialized and will not be updated further.\n'
                  'Please Select ConstantAmbientTemperature if this is not desired.\n')
        self.__ambient_thermal_model = ambient_thermal_model
        self.__system_temperature = self.__ambient_thermal_model.get_initial_temperature()  # K
        self.__air_specific_heat = 1006  # J/kgK, cp (at constant pressure)
        # this is the internal air temperature within the container. Initialized with ambient temperature

    def calculate_temperature(self, time, state: SystemState, states: [SystemState]):
        self.__system_temperature = self.__ambient_thermal_model.get_temperature(time)
        if isinstance(self.__ambient_thermal_model, UserBatteryTemperatureProfile):
            # setting storage technology temperature for SIMSES simulation and plotting
            for storage_technology in self.__storage_technologies:
                storage_technology.state.temperature = self.__system_temperature

    def get_auxiliaries(self) -> [Auxiliary]:
        return list()

    def get_temperature(self):
        return self.__system_temperature

    def get_ambient_temperature(self) -> float:
        return self.__system_temperature

    def get_solar_irradiation_thermal_load(self) -> float:
        return 0.0

    def get_hvac_thermal_power(self) -> float:
        return 0.0

    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for the AmbientThermalModel and
        SolarIrradiationModel
        """
        pass

    def update_air_parameters(self):
        pass

    def get_ol_temperature(self) -> float:
        pass

    def get_il_temperature(self) -> float:
        pass

