from datetime import datetime

import numpy
from pytz import timezone

from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.economic.revenue_stream.abstract_revenue_stream import RevenueStream
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.commons.config.analysis.economic import EconomicAnalysisConfig


class ElectricityConsumptionRevenueStream(RevenueStream):

    """" Calculates the yearly costs for electrictiy consumption for electrolyzer"""

    __UTC: timezone = timezone('UTC')
    __BERLIN: timezone = timezone('Europe/Berlin')

    def __init__(self, energy_management_data: EnergyManagementData, system_data: SystemData, economic_analysis_config: EconomicAnalysisConfig):
        super().__init__(energy_management_data, system_data, economic_analysis_config)
        self.__electricity_price_grid = economic_analysis_config.electricity_price
        self.__electricity_price_renewable = economic_analysis_config.renewable_electricity_price
        self.__cashflow_list = []
        self.__grid_cost_list = []
        self.__renewable_cost_list = []
        self.__Ws_to_kWh = 1/1000 * 1/3600
        self.__shorter_than_one_year = True

    def get_cashflow(self) -> numpy.ndarray:
        time: numpy.ndarray = self._energy_management_data.time
        timestep = time[1] - time[0]
        total_power_system: numpy.ndarray = self._system_data.power
        renewable_power_total: numpy.ndarray = self._energy_management_data.pv_power
        grid_power = total_power_system - renewable_power_total
        renewable_power_used = numpy.add(renewable_power_total, grid_power.clip(max=0))

        cost_renewable_energy_per_timestep = numpy.asarray([power * self.__electricity_price_renewable if power >= 0
                                                            else 0 for power in renewable_power_used]) * timestep * self.__Ws_to_kWh
        cost_grid_power_per_timestep = numpy.asarray([power * self.__electricity_price_grid if power >= 0 else 0 for
                                                      power in grid_power]) * timestep * self.__Ws_to_kWh

        # divide into list for each project year
        self.__grid_cost_list = self.cash_time_series_to_project_years(cost_grid_power_per_timestep, time)
        self.__grid_cost_list = [-1 * x for x in self.__grid_cost_list]

        self.__renewable_cost_list = self.cash_time_series_to_project_years(cost_renewable_energy_per_timestep,time)
        self.__renewable_cost_list = [-1*x for x in self.__renewable_cost_list]

        self.__cashflow_list = []
        for g, r in zip(self.__grid_cost_list, self.__renewable_cost_list):
            self.__cashflow_list.append(g+r)
        return numpy.array(self.__cashflow_list)

    def __get_next_billing_year(self, date: datetime) -> datetime:
        """Returns begin of following year 20xx-01-01 00:00:00"""
        return date.replace(year=date.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    def get_evaluation_results(self) -> [EvaluationResult]:
        key_results: [EvaluationResult] = list()
        key_results.append(EvaluationResult(Description.Economical.ElectricityConsumption.ELECTRICITY_COST_GRID,
                                            Unit.EURO, sum(self.__grid_cost_list)))
        key_results.append(EvaluationResult(Description.Economical.ElectricityConsumption.ELECTRICITY_COST_RENEWABLE,
                                            Unit.EURO, sum(self.__renewable_cost_list)))
        key_results.append(EvaluationResult(Description.Economical.ElectricityConsumption.TOTAL_ELECTRICITY_COST,
                                            Unit.EURO, sum(self.__cashflow_list)))
        return key_results

    def get_assumptions(self) -> [EvaluationResult]:
        assumptions: [EvaluationResult] = list()
        assumptions.append(EvaluationResult(Description.Economical.ElectricityConsumption.ELECTRICITY_COST_RENEWABLE,
                                            Unit.EURO_PER_KWH, self.__electricity_price_renewable))
        assumptions.append(EvaluationResult(Description.Economical.ElectricityConsumption.ELECTRICITY_COST_GRID,
                                            Unit.EURO_PER_KWH, self.__electricity_price_grid))
        return assumptions


    def close(self):
        pass