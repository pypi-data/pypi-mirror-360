from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.file import FileProfile
from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel
from simses.commons.config.simulation.profile import ProfileConfig


class UserBatteryTemperatureProfile(AmbientThermalModel):

    """
    UserBatteryTemperatureProfile reads a user-defined battery temperature profile for the specified battery.
    A temperature value for each timestep is read and updated in the state of the storage technology
    """

    def __init__(self, profile_config: ProfileConfig, general_config: GeneralSimulationConfig):
        super().__init__()
        self.__start_time = general_config.start
        self.__file = FileProfile(general_config, profile_config.battery_temperature_profile_file)
        self.__profile_config: ProfileConfig = profile_config
        self.__general_config: GeneralSimulationConfig = general_config

    def get_temperature(self, time) -> float:
        temp_c = self.__file.next(time)  # in °C
        temp_k = temp_c + 273.15  # in K
        return temp_k

    def get_initial_temperature(self) -> float:
        return self.get_temperature(self.__start_time)  # in K

    def create_instance(self) -> AmbientThermalModel:
        """
        reinstantiates the AmbientThermalModel
        :return: AmbientThermalModel
        """
        return UserBatteryTemperatureProfile(self.__profile_config, self.__general_config)

    def close(self):
        self.__file.close()