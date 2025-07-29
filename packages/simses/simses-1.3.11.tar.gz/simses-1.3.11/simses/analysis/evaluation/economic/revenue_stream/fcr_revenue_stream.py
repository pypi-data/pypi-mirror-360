import numpy as np

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.abstract_revenue_stream import RevenueStream
from simses.analysis.evaluation.result import EvaluationResult, Unit, Description
from simses.commons.config.analysis.economic import EconomicAnalysisConfig
from simses.commons.config.analysis.market import MarketProfileConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.log import Logger
from simses.commons.profile.economic.constant import ConstantPrice
from simses.commons.profile.economic.fcr import FcrMarketProfile
from simses.commons.profile.economic.market import MarketProfile


class FCRRevenue(RevenueStream):

    def __init__(self, energy_management_data: EnergyManagementData, system_data: SystemData,
                 economic_analysis_config: EconomicAnalysisConfig, general_config: GeneralSimulationConfig,
                 market_profile_config: MarketProfileConfig):
        super().__init__(energy_management_data, system_data, economic_analysis_config)
        self.__log: Logger = Logger(type(self).__name__)
        if economic_analysis_config.fcr_use_price_timeseries:
            self.__fcr_price_profile: MarketProfile = FcrMarketProfile(general_config, market_profile_config)
        else:
            self.__fcr_price_profile: MarketProfile = ConstantPrice(economic_analysis_config.fcr_price)
        self._energy_management_data: EnergyManagementData = energy_management_data
        self.__system_data: SystemData = system_data
        self.__fcr_power_avg = np.array([])
        self.__fcr_price_avg = np.array([])
        self.__fcr_revenue = np.array([])
        self.day_to_sec = 60 * 60 * 24
        self.year_to_sec = self.day_to_sec * 365

        self.__simulation_start = general_config.start
        self.__simulation_end = general_config.end

    def get_cashflow(self) -> np.ndarray:
        time_series = self._energy_management_data.time
        fcr_power_series = abs(self._energy_management_data.fcr_max_power)
        fcr_price_series = []
        cashflow_time_series = []
        fcr_price_scaling_factor_day_to_second = 1 / 1e3 * 1 / self.day_to_sec
        delta_ts = time_series[1] - time_series[0]
        start = self.__simulation_start
        end = self.__simulation_end
        loop = 0
        t_loop = 0

        for time, fcr_power in zip(time_series, fcr_power_series):
            # calculate adapted time for looped simulations (otherwise price file may be out of bounds)
            if (time - start) // (end - start) > loop:
                self.__fcr_price_profile.initialize_profile()
                loop += 1
                t_loop = time
            adapted_time = time - t_loop
            price = self.__fcr_price_profile.next(adapted_time)
            fcr_price_series.append(price)
            cashflow_time_series.append(delta_ts * fcr_power * price * fcr_price_scaling_factor_day_to_second)

        self.__fcr_power_avg = np.array(
            self.cash_time_series_to_project_years(fcr_power_series, time_series)) * delta_ts / self.year_to_sec / 1000.0  # in kW
        self.__fcr_price_avg = np.array(self.cash_time_series_to_project_years(fcr_price_series, time_series)) * delta_ts / self.year_to_sec
        self.__fcr_revenue = self.cash_time_series_to_project_years(cashflow_time_series, time_series)
        return np.array(self.__fcr_revenue)

    def get_evaluation_results(self) -> [EvaluationResult]:
        key_results: [EvaluationResult] = list()
        key_results.append(EvaluationResult(Description.Economical.FCR.REVENUE_YEARLY, Unit.EURO, self.__fcr_revenue))
        return key_results

    def get_assumptions(self) -> [EvaluationResult]:
        assumptions: [EvaluationResult] = list()
        assumptions.append(EvaluationResult(Description.Economical.FCR.PRICE_AVERAGE, Unit.EURO_PER_KW_DAY, self.__fcr_price_avg))
        assumptions.append(EvaluationResult(Description.Economical.FCR.POWER_BID_AVERAGE, Unit.KILOWATT, self.__fcr_power_avg ))
        return assumptions

    def close(self):
        self.__log.close()
