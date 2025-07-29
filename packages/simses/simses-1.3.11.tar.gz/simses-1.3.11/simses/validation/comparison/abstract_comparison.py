from abc import ABC, abstractmethod
import pandas
import numpy as np
import csv

from simses.commons.log import Logger
from simses.commons.utils.utilities import create_directory_for, convert_to_numerical_array
from simses.commons.config.validation.general import GeneralValidationConfig
from simses.analysis.evaluation.abstract_evaluation import Evaluation

from simses.validation.real_data_evaluation.technical_evaluation import RealDataTechnicalEvaluation
from simses.validation.comparison.result import ComparisonResult


class Comparison(ABC):

    """
    Within the comparison class the comparison of simulation results and the real date
    regarding system and each storage technology is conducted. It provides results
    in form of figures and the actual and relative differences in KPIs.
    The comparison calculations are done with the help of evaluation object based on
    the simulation analysis results and real data.
    """

    EXT: str = '.csv'
    KPI: str = 'KPI'
    DEV: str = 'Deviations'
    ACTUAL_DEV: str = 'Actual Deviations'
    RELATIVE_DEV: str = 'Relative Deviations in p.u.'

    def __init__(self, simulation_evaluation: Evaluation, real_data_evaluation: RealDataTechnicalEvaluation, config: GeneralValidationConfig,
                 do_comparison: bool):
        self.__log: Logger = Logger(__name__)
        self.__simulation_evaluation: Evaluation = simulation_evaluation
        self.__real_data_evaluation: RealDataTechnicalEvaluation = real_data_evaluation

        self.__do_comparison: bool = do_comparison
        self.__do_plotting: bool = config.plotting and do_comparison
        self.__export_validation_to_csv: bool = config.export_validation_to_csv and do_comparison
        self.__export_validation_to_batch: bool = config.export_validation_to_batch and do_comparison
        self.__file_name: str = '_'.join([type(self).__name__, self.__real_data_evaluation.get_data().id])

        self.__comparison_results: [ComparisonResult] = list()
        self.__figures: list = list()

    def run(self):
        if self.__do_comparison:
            self.compare()
            if self.__do_plotting:
                self.plot()

    @property
    def should_be_considered(self) -> bool:
        return self.__do_comparison

    @abstractmethod
    def compare(self) -> None:
        pass

    @abstractmethod
    def plot(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    def write_dev_to_csv(self, path: str) -> None:
        if not self.__export_validation_to_csv:
            return
        filename = path + self.__file_name + '_' + self.DEV + self.EXT
        for comparison_result in self.__comparison_results:
            result_value = comparison_result.value
            if isinstance(result_value, dict):
                if any([isinstance(value, list) for value in result_value.values()]):
                    result_dataframe: pandas.DataFrame = comparison_result.to_csv()
                    result_dataframe.to_csv(filename, index=False)

    def write_kpi_to_csv(self, path: str) -> None:
        if not self.__export_validation_to_csv:
            return
        filename = path + self.__file_name + '_' + self.KPI + self.EXT
        for comparison_result in self.__comparison_results:
            result_value = comparison_result.value
            if isinstance(result_value, dict):
                if all([isinstance(value, (int, float, complex)) for value in result_value.values()]):
                    result_dataframe: pandas.DataFrame = comparison_result.to_csv()
                    result_dataframe.to_csv(filename, index=False)
    '''
    def write_to_batch(self, path: str, name: str, run: str):
        if not self.__export_validation_to_batch:
            return
        create_directory_for(path)
        for comparison_result in self.__comparison_results:
            file_name = path + comparison_result.description + self.EXT
            output: list = [name, run, self.get_name(), self.__real_data_evaluation.get_data().id, comparison_result.value, comparison_result.unit]
            self.__append_to_file(file_name, output)
            
    def __append_to_file(self, file_name: str, data: list) -> None:
        try:
            with open(file_name, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(data)
        except FileNotFoundError:
            self.__log.error(file_name + ' could not be found')
    '''

    def get_comparison_results(self) -> [ComparisonResult]:
        return self.__comparison_results

    def get_name(self) -> str:
        return type(self.__real_data_evaluation.get_data()).__name__

    def append_result(self, comparison_result: ComparisonResult) -> None:
        self.__comparison_results.append(comparison_result)

    def extend_figures(self, figures: list) -> None:
        self.__figures.extend(figures)

    def get_simulation_evaluation(self):
        return self.__simulation_evaluation

    def get_validation_evaluation(self):
        return self.__real_data_evaluation

    def merge_deviations_in_dict(self, sim_data, real_data) -> dict:
        """merge the actual and relative difference into a dict"""
        act_dev = Comparison.calc_act_deviations(sim_data, real_data)
        rel_dev = Comparison.calc_rel_deviations(sim_data, real_data)
        dev_dict: dict = {self.ACTUAL_DEV: act_dev, self.RELATIVE_DEV: rel_dev}

        return dev_dict

    @staticmethod
    def get_standard_time_series(time) -> np.ndarray:
        time_array = convert_to_numerical_array(time)
        return time_array - time_array[0]

    @staticmethod
    def calc_act_deviations(sim_data, real_data) -> np.ndarray:
        """calculate the actual difference of two data arrays
        when data are given in list, convert list into numpy data array
        """

        sim_data_array = convert_to_numerical_array(sim_data)
        real_data_array = convert_to_numerical_array(real_data)

        return sim_data_array - real_data_array

    @staticmethod
    def calc_abs_deviations(sim_data, real_data) -> np.ndarray:
        """calculate the absolute difference of two data arrays
        when data are given in list, convert list into numpy data array
        """

        act_dev = Comparison.calc_act_deviations(sim_data, real_data)

        return abs(act_dev)

    @staticmethod
    def calc_rel_deviations(sim_data, real_data) -> np.ndarray:
        """calculate the relative difference of two data arrays
        when data are given in list, convert list into numpy data array
        """

        act_dev = Comparison.calc_act_deviations(sim_data, real_data)
        real_data_array = convert_to_numerical_array(real_data)

        return act_dev/abs(real_data_array)



