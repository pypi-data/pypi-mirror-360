import math
from datetime import datetime

import numpy as np

from simses.commons.config.validation.general import GeneralValidationConfig
from simses.commons.log import Logger
from simses.commons.utils.utilities import format_float
from simses.analysis.data.abstract_data import Data
from simses.analysis.evaluation.technical.technical_evaluation import TechnicalEvaluation

from simses.validation.real_data_evaluation.technical_evaluation import RealDataTechnicalEvaluation
from simses.validation.comparison.result import ComparisonResult, Description, Unit
from simses.validation.comparison.abstract_comparison import Comparison


class TechnicalComparison(Comparison):

    """
    TechnicalComparison is a special comparison class for comparing simulated and real data
    regarding technical KPIs, e.g. efficiency

    """

    def __init__(self, simulation_evaluation: TechnicalEvaluation, real_data_evaluation: RealDataTechnicalEvaluation, config: GeneralValidationConfig):
        super().__init__(simulation_evaluation, real_data_evaluation, config, config.technical_validation)
        self.__sim_technical_evaluation: TechnicalEvaluation = simulation_evaluation
        self.__log: Logger = Logger(type(self).__name__)

    def compare(self) -> None:
        self.append_result(ComparisonResult(Description.Technical.DELTA_ROUND_TRIP_EFFICIENCY, Unit.PERCENTAGE, self.delta_round_trip_efficiency))
        self.append_result(ComparisonResult(Description.Technical.DELTA_ENERGY_THROUGHPUT, Unit.KWH, self.delta_energy_throughput))

        self.append_result(ComparisonResult(Description.Technical.DELTA_MEAN_SOC, Unit.PERCENTAGE, self.delta_mean_soc))
        self.append_result(ComparisonResult(Description.Technical.DELTA_MAX_SOC, Unit.PERCENTAGE, self.delta_max_soc))
        self.append_result(ComparisonResult(Description.Technical.DELTA_MIN_SOC, Unit.PERCENTAGE, self.delta_min_soc))

        self.append_result(ComparisonResult(Description.Technical.DELTA_NUMBER_CHANGES_SIGNS, Unit.NONE, self.delta_changes_of_sign))
        self.append_result(ComparisonResult(Description.Technical.DELTA_RESTING_TIME_AVG, Unit.MINUTES, self.delta_resting_times))
        self.append_result(ComparisonResult(Description.Technical.DELTA_ENERGY_CHANGES_SIGN, Unit.PERCENTAGE, self.delta_energy_swapsign))
        self.append_result(ComparisonResult(Description.Technical.DELTA_FULFILLMENT_AVG, Unit.PERCENTAGE, self.delta_average_fulfillment))

    def plot(self) -> None:
        pass

    @property
    def delta_power(self) -> dict:
        sim_data: Data = self.__sim_technical_evaluation.get_data()
        real_data: Data = self.__real_data_evaluation.get_data()

        sim_standard_time = Comparison.get_standard_time_series(sim_data.time)
        real_standard_time = Comparison.get_standard_time_series(real_data.time)

        sim_power = sim_data.power
        real_power = real_data.power

        sim_power_interp = np.interp(real_standard_time, sim_standard_time, sim_power)

        return self.merge_deviations_in_dict(sim_power_interp, real_power)

    @property
    def delta_soc(self) -> dict:
        sim_data: Data = self.__sim_technical_evaluation.get_data()
        real_data: Data = self.__real_data_evaluation.get_data()

        sim_standard_time = Comparison.get_standard_time_series(sim_data.time)
        real_standard_time = Comparison.get_standard_time_series(real_data.time)

        sim_soc_in_pct = sim_data.soc * 100.
        real_soc_in_pct = real_data.soc * 100.

        sim_soc_in_pct_interp = np.interp(real_standard_time, sim_standard_time, sim_soc_in_pct)

        return self.merge_deviations_in_dict(sim_soc_in_pct_interp, real_soc_in_pct)

    @property
    def delta_round_trip_efficiency(self) -> dict:
        """
        Calculates the delta round trip efficiency of the system/battery

        """
        sim_efficiency = self.__sim_technical_evaluation.round_trip_efficiency
        real_efficiency = self.__real_data_evaluation.round_trip_efficiency

        return self.merge_deviations_in_dict(sim_efficiency, real_efficiency)

    @property
    def delta_energy_throughput(self) -> dict:
        sim_energy_throughput = self.__sim_technical_evaluation.energy_throughput
        real_energy_throughput = self.__real_data_evaluation.energy_throughput

        return self.merge_deviations_in_dict(sim_energy_throughput, real_energy_throughput)

    @property
    def delta_max_soc(self) -> dict:
        """
        Calculates the delta max SOC of the system/battery

        """
        sim_max_soc = self.__sim_technical_evaluation.max_soc
        real_max_soc = self.__real_data_evaluation.max_soc

        return self.merge_deviations_in_dict(sim_max_soc, real_max_soc)

    @property
    def delta_mean_soc(self) -> dict:
        """
        Calculates the delta mean SOC of the system/battery

        """
        sim_mean_soc = self.__sim_technical_evaluation.mean_soc
        real_mean_soc = self.__real_data_evaluation.mean_soc

        return self.merge_deviations_in_dict(sim_mean_soc, real_mean_soc)

    @property
    def delta_min_soc(self) -> dict:
        """
        Calculates the delta min SOC of the system/battery

        """
        sim_min_soc = self.__sim_technical_evaluation.min_soc
        real_min_soc = self.__real_data_evaluation.min_soc

        return self.merge_deviations_in_dict(sim_min_soc, real_min_soc)

    @property
    def delta_changes_of_sign(self) -> dict:
        """
        Calculates differences in the average number of changes of sign per day

        """
        sim_daily_changes_of_sign = self.__sim_technical_evaluation.changes_of_sign
        real_daily_changes_of_sign = self.__real_data_evaluation.changes_of_sign

        return self.merge_deviations_in_dict(sim_daily_changes_of_sign, real_daily_changes_of_sign)

    @property
    def delta_resting_times(self) -> dict:
        """
        Calculates differences in the average length of resting time of the system/battery

        """
        sim_resting_time = self.__sim_technical_evaluation.resting_times
        real_resting_time = self.__real_data_evaluation.resting_times

        return self.merge_deviations_in_dict(sim_resting_time, real_resting_time)

    @property
    def delta_energy_swapsign(self) -> dict:
        """
        Calculates differences in the average positive (charged) energy between changes of sign

        """
        sim_energy_swapsign = self.__sim_technical_evaluation.energy_swapsign
        real_energy_swapsign = self.__real_data_evaluation.energy_swapsign

        return self.merge_deviations_in_dict(sim_energy_swapsign, real_energy_swapsign)

    @property
    def delta_average_fulfillment(self) -> dict:
        """
        Calculates differences in the average fulfillment factor of the system/battery. How often can the battery/system charge/discharge the desired amount of power.

        """
        sim_avg_ff = self.__sim_technical_evaluation.average_fulfillment
        real_avg_ff = self.__real_data_evaluation.average_fulfillment

        return self.merge_deviations_in_dict(sim_avg_ff, real_avg_ff)

    @property
    def delta_equivalent_full_cycles(self) -> dict:
        """
        Calculates differences in the number of full-equivalent cycles by dividing the amount of charged energy through the initial capacity

        """
        sim_efc = self.__sim_technical_evaluation.equivalent_full_cycles
        real_efc = self.__real_data_evaluation.equivalent_full_cycles

        return self.merge_deviations_in_dict(sim_efc, real_efc)

    @property
    def delta_depth_of_discharges(self) -> dict:
        """
        Calculates differences in the average depth of cycles in discharge direction

        """
        sim_doc = self.__sim_technical_evaluation.depth_of_discharges
        real_doc = self.__real_data_evaluation.depth_of_discharges

        return self.merge_deviations_in_dict(sim_doc, real_doc)

    def close(self) -> None:
        self.__log.close()
