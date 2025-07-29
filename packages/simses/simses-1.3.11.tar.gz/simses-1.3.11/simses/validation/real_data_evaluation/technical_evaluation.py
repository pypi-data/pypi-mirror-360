from simses.commons.log import Logger
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.config.validation.general import GeneralValidationConfig

from simses.analysis.data.abstract_data import Data
from simses.analysis.evaluation.technical.technical_evaluation import TechnicalEvaluation


class RealDataTechnicalEvaluation(TechnicalEvaluation):

    def __init__(self, data: Data, validation_config: GeneralValidationConfig, analysis_config: GeneralAnalysisConfig):
        super().__init__(data, analysis_config)
        self.__validation_configuration: GeneralValidationConfig = validation_config
        self.__log: Logger = Logger(type(self).__name__)


