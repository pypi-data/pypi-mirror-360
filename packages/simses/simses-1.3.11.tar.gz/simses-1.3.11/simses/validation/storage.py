from configparser import ConfigParser
from os.path import dirname, basename
from simses.analysis.evaluation.abstract_evaluation import Evaluation

from simses.commons.config.validation.general import GeneralValidationConfig
from simses.commons.log import Logger
from simses.validation.factory import ValidationFactory
from simses.validation.comparison.abstract_comparison import Comparison
from simses.validation.comparison.merger import ComparisonMerger


class StorageValidation:

    def __init__(self, path: str, config: ConfigParser, batch_dir: str, version: str):
        """
        Constructor of StorageValidation

        Parameters
        ----------
        path :
            path to simulation result folder
        config :
            Optional configs taken into account overwriting values from provided config file
        batch_dir :
            Absolute path of result folder for comparing multiple simulation results
        version :
            current simses version
        """
        self.__path: str = path
        self.__version: str = version
        self.__batch_path: str = batch_dir  # str(Path(self.__path).parent).replace('\\','/') + '/' + BATCH_DIR
        self.__simulation_name: str = basename(dirname(self.__path))
        self.__log: Logger = Logger(__name__)
        self.__config: GeneralValidationConfig = GeneralValidationConfig(config)
        self.__validation_config: ConfigParser = config
        self.__simulation_evaluations = None

    def run(self) -> None:
        """
        Executes validation of selected profiles

        Returns
        -------

        """
        result_path: str = self.__config.get_result_for(self.__path)
        factory: ValidationFactory = ValidationFactory(result_path, self.__validation_config, self.__version, self.__simulation_evaluations)
        comparisons: [Comparison] = factory.create_comparisons()
        comparison_merger: ComparisonMerger = factory.create_comparison_merger()
        files_to_transpose: [str] = list()
        self.__log.info('Entering validation')
        for comparison in comparisons:
            self.__log.info('Running validation ' + type(comparison).__name__)
            comparison.run()
            comparison.write_dev_to_csv(result_path)
            comparison.write_kpi_to_csv(result_path)
            '''
            comparison.write_to_batch(path=self.__batch_path, name=self.__simulation_name, run=basename(dirname(result_path)))
            files_to_transpose.extend(comparison.get_files_to_transpose())
            '''
            comparison.close()
        #Evaluation.transpose_files(files_to_transpose)
        self.__config.write_config_to(result_path)
        comparison_merger.merge(comparisons)
        factory.close()
        self.close()

    def receive_simulation_evaluations(self, evaluations: [Evaluation]):
        self.__simulation_evaluations = evaluations

    def close(self) -> None:
        """
        Closing all resources in analysis
        Returns
        -------

        """
        self.__log.close()
