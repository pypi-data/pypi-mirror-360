import os
from configparser import ConfigParser

from simses.commons.log import Logger
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.config.validation.general import GeneralValidationConfig
from simses.commons.config.validation.validation_profile import ValidationProfileConfig

from simses.analysis.data.abstract_data import Data
from simses.analysis.evaluation.abstract_evaluation import Evaluation
from simses.analysis.evaluation.technical.system import SystemTechnicalEvaluation

from simses.validation.validation_data.load_real_data import LoadRealData
from simses.validation.validation_data.real_system import RealSystemData
from simses.validation.real_data_evaluation.system import RealDataSystemTechnicalEvaluation
from simses.validation.comparison.abstract_comparison import Comparison
from simses.validation.comparison.technical.system import SystemTechnicalComparison
from simses.validation.comparison.merger import ComparisonMerger


class ValidationFactory:

    def __init__(self, path: str, config: ConfigParser, version: str, simulation_evaluations: [Evaluation]):
        self.__log: Logger = Logger(type(self).__name__)
        self.__result_path: str = path
        self.__simulation_result_path: str = os.path.abspath(os.path.dirname(path))
        self.__version: str = version
        self.__simulation_config: GeneralSimulationConfig = GeneralSimulationConfig(config, path=self.__simulation_result_path)
        self.__analysis_config: GeneralAnalysisConfig = GeneralAnalysisConfig(config, self.__simulation_result_path)
        self.__validation_config: GeneralValidationConfig = GeneralValidationConfig(config)
        self.__validation_profile_config: ValidationProfileConfig = ValidationProfileConfig(config)
        self.__do_plotting: bool = self.__validation_config.plotting

        self.__simulation_evaluations = simulation_evaluations

        self.__do_system_validation: bool = self.__validation_config.system_validation
        '''
        self.__do_lithium_ion_validation: bool = self.__validation_config.lithium_ion_validation
        self.__do_redox_flow_validation: bool = self.__validation_config.redox_flow_validation
        self.__do_hydrogen_validation: bool = self.__validation_config.hydrogen_validation
        self.__do_site_level_validation: bool = self.__validation_config.site_level_validation

        try:
            self.__energy_management_data: EnergyManagementData = EnergyManagementData.get_system_data(self.__result_path, self.__simulation_config)[0]
        except IndexError:
            self.__log.warn('No energy management data found!')
            self.__energy_management_data = None
        '''

    def create_comparisons(self) -> [Comparison]:
        real_data_evaluation_list = self.create_real_data_evaluations()
        comparisons: [Comparison] = list()
        for real_data_evaluation in real_data_evaluation_list:
            if isinstance(real_data_evaluation, RealDataSystemTechnicalEvaluation):
                if self.__do_system_validation:
                    sim_evaluation = [i for i in self.__simulation_evaluations if isinstance(i, SystemTechnicalEvaluation)]
                    if len(sim_evaluation):
                        comparisons.append(SystemTechnicalComparison(sim_evaluation[0], real_data_evaluation, self.__validation_config, self.__result_path))
                    else:
                        print('No ' + SystemTechnicalEvaluation.__name__ + ' for simulation was done. Validation aborted.')

        return comparisons

    def __create_real_data_list(self) -> [Data]:
        real_data_loaded: LoadRealData = LoadRealData(self.__validation_profile_config)
        data_list: [Data] = list()
        data_list.append(RealSystemData(self.__simulation_config, self.__validation_config, real_data_loaded.data, real_data_loaded.unit))

        for data in data_list:
            self.__log.info('Created ' + type(data).__name__)
        return data_list

    def create_real_data_evaluations(self) -> [Evaluation]:
        """
        Currently only support the validation of power profile of the ESS
        In the future the code can be extended for validation of other profiles of the storage system
        based on e.g. simulated LithiumIonState data

        """

        data_list: [Data] = self.__create_real_data_list()
        evaluations: [Evaluation] = list()
        for data in data_list:
            if isinstance(data, RealSystemData):
                if self.__do_system_validation:
                    evaluations.append(RealDataSystemTechnicalEvaluation(data, self.__validation_config, self.__analysis_config))

        return evaluations

    def create_comparison_merger(self) -> ComparisonMerger:
        return ComparisonMerger(self.__result_path, self.__validation_config, self.__version)

    def close(self):
        self.__log.close()
