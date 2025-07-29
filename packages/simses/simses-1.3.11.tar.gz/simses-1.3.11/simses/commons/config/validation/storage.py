from configparser import ConfigParser
from simses.commons.config.validation.validation_config import ValidationConfig


class StorageValidationConfig(ValidationConfig):
    """
    Storage validation configs
    """

    SECTION: str = 'STORAGE_VALIDATION'
    DC_POWER_STORAGE_VALIDATION: str = 'DC_POWER_STORAGE_VALIDATION'
    AC_POWER_DELIVERED_VALIDATION: str = 'AC_POWER_DELIVERED_VALIDATION'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    @property
    def dc_power_storage_validation(self) -> bool:
        """Returns boolean value for validation of dc power of storage modul after analyzing simulation results"""
        return self.get_property(self.SECTION, self.DC_POWER_STORAGE_VALIDATION) in ['True']

    @property
    def ac_power_delivered_validation(self) -> bool:
        """Returns boolean value for validation of delivered ac power after analyzing simulation results"""
        return self.get_property(self.SECTION, self.AC_POWER_DELIVERED_VALIDATION) in ['True']