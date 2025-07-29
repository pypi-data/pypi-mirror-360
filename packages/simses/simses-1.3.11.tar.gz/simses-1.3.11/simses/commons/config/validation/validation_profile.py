from configparser import ConfigParser
from simses.commons.config.validation.validation_config import ValidationConfig


class ValidationProfileConfig(ValidationConfig):

    """
    Validation profile configs
    """

    SECTION: str = 'VALIDATION_PROFILE'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    @property
    def validation_profile_dir(self) -> str:
        """Returns directory of validation profiles from __validation_config file_name"""
        return self.get_data_path(self.get_property(self.SECTION, 'VALIDATION_PROFILE_DIR'))

    @property
    def data_source_name(self) -> str:
        """
           Returns file name of data source under the directory of validation profiles
           from __validation_config file_name
        """
        return self.get_data_path(self.get_property(self.SECTION, 'DATA_SOURCE_NAME'))

    @property
    def real_ac_power_delivered_profile(self) -> str:
        """Returns file name of storage power profile from __validation_config file_name"""
        return self.validation_profile_dir + self.data_source_name + self.get_property(self.SECTION, 'AC_POWER_DELIVERED_FILE')

    @property
    def real_dc_power_storage_profile(self) -> str:
        """Returns file name of storage power profile from __validation_config file_name"""
        return self.validation_profile_dir + self.data_source_name + self.get_property(self.SECTION, 'DC_POWER_STORAGE_FILE')

    @property
    def real_dc_power_intermediate_profile(self) -> str:
        """Returns file name of storage power profile from __validation_config file_name"""
        return self.validation_profile_dir + self.data_source_name + self.get_property(self.SECTION, 'DC_POWER_INTERMEDIATE_FILE')

    @property
    def real_storage_soc_profile(self) -> str:
        """ Return file name of storage SOE profile from __validation_config file_name"""
        return self.validation_profile_dir + self.data_source_name + self.get_property(self.SECTION, 'STORAGE_SOC_FILE')

    @property
    def real_grid_profile(self) -> str:
        """ Return file name of grid profile from __validation_config file_name"""
        return self.validation_profile_dir + self.data_source_name + self.get_property(self.SECTION, 'GRID_PROFILE')
