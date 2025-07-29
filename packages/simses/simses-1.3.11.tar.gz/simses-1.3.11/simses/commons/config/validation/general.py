import os
import pathlib
from configparser import ConfigParser
from simses.commons.config.validation.validation_config import ValidationConfig
from simses.commons.utils.utilities import convert_path_codec


class GeneralValidationConfig(ValidationConfig):

    """
    General validation configs
    """
    SECTION: str = 'GENERAL'
    SIMULATION: str = 'SIMULATION'
    VALIDATION_NAME: str = 'VALIDATION_NAME'
    SYSTEM_LABEL: str = 'SYSTEM_LABEL'
    EXPORT_VALIDATION_TO_CSV: str = 'EXPORT_VALIDATION_TO_CSV'
    PRINT_RESULTS_TO_CONSOLE: str = 'PRINT_VALIDATION_TO_CONSOLE'
    EXPORT_VALIDATION_TO_BATCH: str = 'EXPORT_ANALYSIS_TO_BATCH'
    MERGE_VALIDATION: str = 'MERGE_ANALYSIS'
    PLOTTING: str = 'PLOTTING'
    TECHNICAL_VALIDATION: str = 'TECHNICAL_VALIDATION'

    SYSTEM_VALIDATION: str = 'SYSTEM_VALIDATION'
    LITHIUM_ION_VALIDATION: str = 'LITHIUM_ION_VALIDATION'
    REDOX_FLOW_VALIDATION: str = 'REDOX_FLOW_VALIDATION'
    HYDROGEN_VALIDATION: str = 'HYDROGEN_VALIDATION'
    SITE_LEVEL_VALIDATION: str = 'SITE_LEVEL_VALIDATION'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    def get_result_for(self, path: str) -> str:
        """Returns name of the simulation to validate."""
        simulation = convert_path_codec(self.get_property(self.SECTION, self.SIMULATION))
        if simulation == 'LATEST':
            result_dirs = list()
            tmp_dirs = os.listdir(path)
            # res = filter(os.path.isdir, tmp_dirs)
            for tmp_dir in tmp_dirs:
                if os.path.isdir(path + tmp_dir):
                    result_dirs.append(path + tmp_dir + '/')
            return max(result_dirs, key=os.path.getmtime) + 'validation/'
        elif os.path.isabs(simulation):
            return pathlib.Path(simulation).as_posix() + '/validation/'
        else:
            return path + simulation + '/validation/'

    @property
    def validation_name(self) -> str:
        name = self.get_property(self.SECTION, self.VALIDATION_NAME)
        return name.replace('_', ' ')

    @property
    def system_label(self) -> str:
        label = self.get_property(self.SECTION, self.SYSTEM_LABEL)
        return label.replace('_', ' ')

    @property
    def export_validation_to_csv(self) -> bool:
        """Defines if analysis results are to be exported to csv files"""
        return self.get_property(self.SECTION, self.EXPORT_VALIDATION_TO_CSV) in ['True']

    @property
    def print_result_to_console(self) -> bool:
        """Defines if analysis results are to be printed to console"""
        return self.get_property(self.SECTION, self.PRINT_RESULTS_TO_CONSOLE) in ['True']

    @property
    def export_validation_to_batch(self) -> bool:
        """Defines if analysis results are written to batch files"""
        return self.get_property(self.SECTION, self.EXPORT_VALIDATION_TO_BATCH) in ['True']

    @property
    def merge_validation(self) -> bool:
        """Defines if analysis results are merged"""
        return self.get_property(self.SECTION, self.MERGE_VALIDATION) in ['True']

    @property
    def technical_validation(self) -> bool:
        """Returns boolean value for matplot_plotting after the simulation"""
        return self.get_property(self.SECTION, self.TECHNICAL_VALIDATION) in ['True']

    @property
    def plotting(self) -> bool:
        """Returns boolean value for matplot_plotting after the simulation"""
        return self.get_property(self.SECTION, self.PLOTTING) in ['True']

    @property
    def logo_file(self) -> str:
        return self.get_data_path(self.get_property(self.SECTION, 'LOGO_FILE'))

    @property
    def system_validation(self) -> bool:
        """Returns boolean value for system analysis after the simulation"""
        return self.get_property(self.SECTION, self.SYSTEM_VALIDATION) in ['True']

    @property
    def lithium_ion_validation(self) -> bool:
        """Returns boolean value for lithium-ion validation after the simulation"""
        return self.get_property(self.SECTION, self.LITHIUM_ION_VALIDATION) in ['True']

    @property
    def redox_flow_validation(self) -> bool:
        """Returns boolean value for redox flow validation after the simulation"""
        return self.get_property(self.SECTION, self.REDOX_FLOW_VALIDATION) in ['True']

    @property
    def hydrogen_validation(self) -> bool:
        """Returns boolean value for hydrogen validation after the simulation"""
        return self.get_property(self.SECTION, self.HYDROGEN_VALIDATION) in ['True']

    @property
    def site_level_validation(self) -> bool:
        """Returns boolean value for grid power validation after the simulation"""
        return self.get_property(self.SECTION, self.SITE_LEVEL_VALIDATION) in ['True']




