from configparser import ConfigParser
from simses.commons.config.simulation.simulation_config import SimulationConfig, clean_split
from simses.commons.profile.file import FileProfile
from simses.commons.profile.power.file import FilePowerProfile
from simses.commons.utils.utilities import format_float


class ProfileConfig(SimulationConfig):
    """
    Profile specific configs
    """

    SECTION: str = 'PROFILE'

    POWER_PROFILE_DIR: str = 'POWER_PROFILE_DIR'
    TECHNICAL_PROFILE_DIR: str = 'TECHNICAL_PROFILE_DIR'
    THERMAL_PROFILE_DIR: str = 'THERMAL_PROFILE_DIR'
    LOAD_MAT_FILE: str = 'LOAD_MAT_FILE'
    LOAD_PROFILE: str = 'LOAD_PROFILE'
    FREQUENCY_PROFILE: str = 'FREQUENCY_PROFILE'
    LOAD_FORECAST_PROFILE: str = 'LOAD_FORECAST_PROFILE'
    SOC_PROFILE: str = 'SOC_PROFILE'
    GENERATION_MAT_FILE: str = 'GENERATION_MAT_FILE'
    GENERATION_PROFILE: str = 'GENERATION_PROFILE'
    V2G_PROFILE: str = 'V2G_PROFILE'
    BINARY_PROFILE: str = 'BINARY_PROFILE'
    V2G_POOL_AVAILABILITY_PROFILE: str = 'V2G_POOL_AVAILABILITY_PROFILE'

    AMBIENT_TEMPERATURE_PROFILE: str = 'AMBIENT_TEMPERATURE_PROFILE'
    BATTERY_TEMPERATURE_PROFILE: str = 'BATTERY_TEMPERATURE_PROFILE'
    GLOBAL_HORIZONTAL_IRRADIATION_PROFILE: str = 'GLOBAL_HORIZONTAL_IRRADIATION_PROFILE'
    LOAD_PROFILE_SCALING: str = 'LOAD_PROFILE_SCALING'
    LOAD_SCALING_FACTOR: str = 'LOAD_SCALING_FACTOR'
    GENERATION_PROFILE_SCALING: str = 'GENERATION_PROFILE_SCALING'
    GENERATION_SCALING_FACTOR: str = 'GENERATION_SCALING_FACTOR'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    @property
    def power_profile_dir(self) -> str:
        """Returns directory of power profiles from __analysis_config file_name"""
        return self.get_data_path(self.get_property(self.SECTION, self.POWER_PROFILE_DIR))

    @property
    def technical_profile_dir(self) -> str:
        """Returns directory of frequency profiles from __analysis_config file_name"""
        return self.get_data_path(self.get_property(self.SECTION, self.TECHNICAL_PROFILE_DIR))

    @property
    def thermal_profile_dir(self) -> str:
        """Returns directory of thermal profiles from __analysis_config file_name"""
        return self.get_data_path(self.get_property(self.SECTION, self.THERMAL_PROFILE_DIR))

    @property
    def load_profile_file(self) -> str:
        """ Return selected load profile file"""
        return self.power_profile_dir + self.get_property(self.SECTION, self.LOAD_PROFILE)

    @property
    def load_mat_file(self) -> str:
        """ Return selected load profile file"""
        return self.get_property(self.SECTION, self.LOAD_MAT_FILE)

    @property
    def frequency_file(self) -> str:
        """Returns frequency profile file_name name from __analysis_config file_name"""
        return self.technical_profile_dir + self.get_property(self.SECTION, self.FREQUENCY_PROFILE)

    @property
    def load_forecast_file(self) -> str:
        """Returns frequency profile file_name name from __analysis_config file_name"""
        return self.technical_profile_dir + self.get_property(self.SECTION, self.LOAD_FORECAST_PROFILE)

    @property
    def soc_file(self) -> str:
        """Returns soc profile file_name"""
        return self.technical_profile_dir + self.__get_soc_profile()[0]

    @property
    def soc_file_value(self) -> int:
        """Returns soc profile value index"""
        try:
            return int(self.__get_soc_profile()[1])
        except IndexError:
            return 1

    def __get_soc_profile(self) -> [str]:
        return clean_split(self.get_property(self.SECTION, self.SOC_PROFILE), ',')

    @property
    def generation_profile_file(self) -> str:
        """ Return PV generation profile file_name name from __analysis_config file_name"""
        return self.power_profile_dir + self.get_property(self.SECTION, self.GENERATION_PROFILE)

    @property
    def generation_mat_file(self) -> str:
        """ Return selected load profile file"""
        return self.get_property(self.SECTION, self.GENERATION_MAT_FILE)

    @property
    def v2g_profile_file(self) -> str:
        """ Return V2G load profile file_name name from __analysis_config file_name"""
        return self.power_profile_dir + self.get_property(self.SECTION, self.V2G_PROFILE)

    @property
    def binary_profile_file(self) -> str:
        """ Return binary profile file_name name from __analysis_config file_name"""
        return self.technical_profile_dir + self.get_property(self.SECTION, self.BINARY_PROFILE)

    @property
    def v2g_pool_availability_profile_file(self) -> str:
        """ Return binary profile file_name name from __analysis_config file_name"""
        return self.technical_profile_dir + self.get_property(self.SECTION, self.V2G_POOL_AVAILABILITY_PROFILE)

    @property
    def ambient_temperature_profile_file(self) -> str:
        """ Return selected location ambient temperature profile"""
        return self.thermal_profile_dir + self.get_property(self.SECTION, self.AMBIENT_TEMPERATURE_PROFILE)

    @property
    def battery_temperature_profile_file(self) -> str:
        """ Return selected battery temperature profile"""
        return self.thermal_profile_dir + self.get_property(self.SECTION, self.BATTERY_TEMPERATURE_PROFILE)

    @property
    def global_horizontal_irradiation_profile_file(self) -> str:
        """ Return selected location global horizontal irradiation profile"""
        return self.thermal_profile_dir + self.get_property(self.SECTION, self.GLOBAL_HORIZONTAL_IRRADIATION_PROFILE)

    @property
    def load_profile_scaling(self) -> str:
        """
        Returns the type of load scaling to be applied - Either Energy, Power, or False (if disabled) as str
        """
        return self.get_property(self.SECTION, self.LOAD_PROFILE_SCALING)

    @property
    def load_scaling_factor(self) -> float:
        """ Return scaling factor for the load from __analysis_config file_name"""
        scaling_factor: float = float(self.get_property(self.SECTION, self.LOAD_SCALING_FACTOR))
        if str.lower(self.load_profile_scaling) == 'energy':
            return scaling_factor / self.__get_annual_consumption()
        elif str.lower(self.load_profile_scaling) == 'power':
            return scaling_factor / self.__get_peak_power(self.load_profile_file)
        else:
            return 1.0  # no scaling: original values are taken

    @property
    def generation_profile_scaling(self) -> str:
        """
       Returns the type of generation profile scaling to be applied - Energy, Power, or False (if disabled) as str
       """
        return self.get_property(self.SECTION, self.GENERATION_PROFILE_SCALING)

    @property
    def generation_scaling_factor(self) -> float:
        """ Return scaling factor for pv from __analysis_config file_name"""
        scaling_factor: float = float(self.get_property(self.SECTION, self.GENERATION_SCALING_FACTOR))
        if str.lower(self.generation_profile_scaling) == 'power':
            return scaling_factor / self.__get_peak_power(self.generation_profile_file)
        else:
            return 1.0  # no scaling: original values are taken

    def __get_annual_consumption(self) -> float:
        try:
            value: float = self.__get_value_from_header(FilePowerProfile.Header.ANNUAL_CONSUMPTION, self.load_profile_file)
            return value * 1000.0
        except (IndexError, KeyError):
            return 1.0

    def __get_peak_power(self, filename: str) -> float:
        try:
            peak_power: float = self.__get_value_from_header(FilePowerProfile.Header.PEAK_POWER, filename)
            return peak_power * 1000.0  # Wp
        except (IndexError, KeyError):
            print('Searching for peak power in ' + filename + '... \n(This can take a while. In order to speed things '
                  'up you may include the following header to your profile: # ' + FilePowerProfile.Header.PEAK_POWER +
                  ': [your power value].)')
            value: float = FileProfile.get_max_value_of(filename)
            print('Your power value would be: ' + format_float(value / 1000.0, 6) + ' kWp')
            return value

    @staticmethod
    def __get_value_from_header(name: str, file: str) -> float:
        header: dict = FileProfile.get_header_from(file)
        value = float(header[name])
        return value
