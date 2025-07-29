import numpy as np

from simses.commons.utils.utilities import get_standard_norm_for

from simses.analysis.utils import get_min_for, get_max_for
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.technical.system import SystemTechnicalEvaluation
from simses.analysis.evaluation.plotting.axis import Axis
from simses.analysis.evaluation.plotting.plotly_plotting import PlotlyPlotting
from simses.analysis.evaluation.plotting.plotter import Plotting

from simses.validation.validation_data.real_system import RealSystemData
from simses.validation.real_data_evaluation.system import RealDataSystemTechnicalEvaluation
from simses.validation.comparison.abstract_comparison import Comparison
from simses.validation.comparison.technical.technical_comparison import TechnicalComparison
from simses.validation.comparison.result import ComparisonResult, Description, Unit

from simses.commons.config.validation.general import GeneralValidationConfig
from simses.commons.log import Logger
from simses.commons.state.system import SystemState


class SystemTechnicalComparison(TechnicalComparison):
    __power_title = 'Power Profile Validation of System '
    __delta_power_title = 'Power Deviation of System '
    __soc_title = 'SOC Profile Validation of System '
    __delta_soc_title = 'SOC Deviation of System '

    def __init__(self, simulation_evaluation: SystemTechnicalEvaluation, real_data_evaluation: RealDataSystemTechnicalEvaluation, config: GeneralValidationConfig, path: str):
        super().__init__(simulation_evaluation, real_data_evaluation, config)
        self.__log: Logger = Logger(type(self).__name__)
        self.__simulation_evaluation: SystemTechnicalEvaluation = simulation_evaluation
        self.__real_data_evaluation: RealDataSystemTechnicalEvaluation = real_data_evaluation
        self.__sim_system_label: str = self.__simulation_evaluation.get_data().id
        self.__real_system_label: str = self.__real_data_evaluation.get_data().id
        title_extension: str = self.__sim_system_label + ' with data from ' + self.__real_system_label
        title_extension_delta: str = self.__sim_system_label + ' from ' + self.__real_system_label
        self.__power_title += title_extension
        self.__delta_power_title += title_extension_delta
        self.__soc_title += title_extension
        self.__delta_soc_title += title_extension_delta

        self.__result_path = path
        self._set_numpy_err_handling()

    def _set_numpy_err_handling(self):
        """Log numpy's `divide by zero` warnings instead of printing"""

        def err_handler(num_type, flag):
            self.__log.warn("Numpy floating point error (%s), with flag %s" % (num_type, flag))

        np.seterrcall(err_handler)
        np.seterr(all='call')

        # self.__battery_config = storage_system_config
        # self.__test: float = sum([float(storage_system_ac[StorageSystemConfig.AC_SYSTEM_POWER])
        #                         for storage_system_ac in storage_system_config.storage_systems_ac]) * 1e-3
        # self.__system_initial_capacity: float = sum([float(storage_system_config.storage_technologies[storage_system_dc
        #                 [StorageSystemConfig.DC_SYSTEM_STORAGE]][StorageSystemConfig.STORAGE_CAPACITY])
        #                    for storage_system_dc in storage_system_config.storage_systems_dc]) * 1e-3
        # self.__system_initial_capacity: float = self.__get_initial_capacity_from(storage_system_config)

    # def __get_initial_capacity_from(self, storage_system_config: StorageSystemConfig) -> float:
    #     capacity: float = 0.0
    #     storage_technologies: dict = storage_system_config.storage_technologies
    #     for storage_system_dc in storage_system_config.storage_systems_dc:
    #         storage_name: str = storage_system_dc[StorageSystemConfig.DC_SYSTEM_STORAGE]
    #         if storage_name in storage_technologies.keys():
    #             capacity += float(storage_technologies[storage_name][StorageSystemConfig.STORAGE_CAPACITY])
    #     return capacity * 1e-3

    def compare(self):
        super().compare()
        self.append_result(ComparisonResult(Description.Technical.DELTA_AC_DELIVERED, Unit.WATT, self.delta_power))
        self.append_result(ComparisonResult(Description.Technical.DELTA_DC_STORAGE, Unit.WATT, self.delta_dc_power_storage))
        self.append_result(ComparisonResult(Description.Technical.DELTA_SOC, Unit.PERCENTAGE, self.delta_soc))

        self.append_result(ComparisonResult(Description.Technical.SN_DELTA_AC_DELIVERED, Unit.WATT, self.sn_delta_ac_delivered))
        self.append_result(ComparisonResult(Description.Technical.SN_DELTA_SOC, Unit.PERCENTAGE, self.sn_delta_soc))

        self.append_result(ComparisonResult(Description.Technical.DELTA_MAX_AC_DELIVERED, Unit.WATT, self.delta_max_ac_delivered))
        self.append_result(ComparisonResult(Description.Technical.DELTA_MIN_AC_DELIVERED, Unit.WATT, self.delta_min_ac_delivered))

    def plot(self) -> None:
        self.__power_plotting()
        self.__delta_power_plotting()
        self.__soc_plotting()
        self.__delta_soc_plotting()

    def __power_plotting(self):
        sim_data: SystemData = self.__simulation_evaluation.get_data()
        real_data: RealSystemData = self.__real_data_evaluation.get_data()
        plot: Plotting = PlotlyPlotting(title=self.__power_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(sim_data.time), label=SystemState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(sim_data.power, label=' '.join([SystemState.AC_POWER_DELIVERED, self.__sim_system_label]),
                          color=PlotlyPlotting.Color.AC_POWER_BLUE,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(real_data.power, label=' '.join([SystemState.AC_POWER_DELIVERED, self.__real_system_label]),
                          color=PlotlyPlotting.Color.ROYAL_BLUE,
                          linestyle=PlotlyPlotting.Linestyle.DASHED))
        yaxis.append(Axis(sim_data.dc_power_storage, label=' '.join([SystemState.DC_POWER_STORAGE, self.__sim_system_label]),
                          color=PlotlyPlotting.Color.DC_POWER_GREEN,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(real_data.dc_power_storage, label=' '.join([SystemState.DC_POWER_STORAGE, self.__real_system_label]),
                          color=PlotlyPlotting.Color.DARK_CYAN,
                          linestyle=PlotlyPlotting.Linestyle.DASHED))

        plot.lines(xaxis=xaxis, yaxis=yaxis)
        plot.histogram(xaxis=xaxis, yaxis=yaxis)
        self.extend_figures(plot.get_figures())

    def __delta_power_plotting(self):
        sim_data: SystemData = self.__simulation_evaluation.get_data()
        plot: Plotting = PlotlyPlotting(title=self.__delta_power_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(sim_data.time), label=SystemState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(self.delta_power[self.ACTUAL_DEV], label=' in '.join([self.ACTUAL_DEV, SystemState.AC_POWER_DELIVERED]),
                          color=PlotlyPlotting.Color.AC_POWER_BLUE, linestyle=PlotlyPlotting.Linestyle.DOTTED))
        yaxis.append(Axis(self.delta_dc_power_storage[self.ACTUAL_DEV], label=' in '.join([self.ACTUAL_DEV, SystemState.DC_POWER_STORAGE]),
                          color=PlotlyPlotting.Color.DC_POWER_GREEN, linestyle=PlotlyPlotting.Linestyle.DOTTED))
        yaxis.append(Axis(self.delta_power[self.RELATIVE_DEV], label=' in '.join([self.RELATIVE_DEV, SystemState.AC_POWER_DELIVERED]),
                          color=PlotlyPlotting.Color.AC_POWER_BLUE, linestyle=PlotlyPlotting.Linestyle.DASH_DOT))
        yaxis.append(Axis(self.delta_dc_power_storage[self.RELATIVE_DEV], label=' in '.join([self.RELATIVE_DEV, SystemState.DC_POWER_STORAGE]),
                          color=PlotlyPlotting.Color.DC_POWER_GREEN, linestyle=PlotlyPlotting.Linestyle.DASH_DOT))
        plot.lines(xaxis, yaxis, [2, 3])
        self.extend_figures(plot.get_figures())

    def __soc_plotting(self):
        sim_data: SystemData = self.__simulation_evaluation.get_data()
        real_data: RealSystemData = self.__real_data_evaluation.get_data()
        plot: Plotting = PlotlyPlotting(title=self.__soc_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(sim_data.time), label=SystemState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(sim_data.soc, label=' '.join([SystemState.SOC, self.__sim_system_label]),
                          color=PlotlyPlotting.Color.SOC_BLUE, linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(real_data.soc, label=' '.join([SystemState.SOC, self.__real_system_label]),
                          color=PlotlyPlotting.Color.SOC_BLUE, linestyle=PlotlyPlotting.Linestyle.DASHED))
        plot.lines(xaxis, yaxis)
        self.extend_figures(plot.get_figures())

    def __delta_soc_plotting(self):
        sim_data: SystemData = self.__simulation_evaluation.get_data()
        plot: Plotting = PlotlyPlotting(title=self.__delta_soc_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(sim_data.time), label=SystemState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(self.delta_soc[self.ACTUAL_DEV]/.100, label=' in '.join([self.ACTUAL_DEV, SystemState.SOC]),
                          color=PlotlyPlotting.Color.SOC_BLUE, linestyle=PlotlyPlotting.Linestyle.DOTTED))
        yaxis.append(Axis(self.delta_soc[self.RELATIVE_DEV], label=' in '.join([self.RELATIVE_DEV, SystemState.SOC]),
                          color=PlotlyPlotting.Color.SOC_BLUE, linestyle=PlotlyPlotting.Linestyle.DASH_DOT))
        plot.lines(xaxis, yaxis)
        plot.histogram(xaxis=xaxis, yaxis=yaxis)
        self.extend_figures(plot.get_figures())

    @property
    def delta_dc_power_storage(self) -> dict:
        sim_data: SystemData = self.__sim_technical_evaluation.get_data()
        real_data: RealSystemData = self.__real_data_evaluation.get_data()

        sim_standard_time = Comparison.get_standard_time_series(sim_data.time)
        real_standard_time = Comparison.get_standard_time_series(real_data.time)

        sim_power = sim_data.dc_power_storage
        real_power = real_data.dc_power_storage

        sim_power_interp = np.interp(real_standard_time, sim_standard_time, sim_power)

        return self.merge_deviations_in_dict(sim_power_interp, real_power)

    @property
    def sn_delta_ac_delivered(self) -> float:

        return get_standard_norm_for(self.delta_power)

    @property
    def sn_delta_soc(self) -> float:

        return get_standard_norm_for(self.delta_soc)

    @property
    def delta_max_ac_delivered(self) -> dict:
        sim_max_ac_delivered = get_max_for(self.__simulation_evaluation.get_data().soc)
        real_max_ac_delivered = get_max_for(self.__real_data_evaluation.get_data().soc)

        return self.merge_deviations_in_dict(sim_max_ac_delivered, real_max_ac_delivered)

    @property
    def delta_min_ac_delivered(self) -> dict:
        sim_min_ac_delivered = get_min_for(self.__simulation_evaluation.get_data().soc)
        real_min_ac_delivered = get_min_for(self.__real_data_evaluation.get_data().soc)

        return self.merge_deviations_in_dict(sim_min_ac_delivered, real_min_ac_delivered)

    # @property
    # def capacity_remaining(self) -> float:
    #     data: SystemData = self.get_data()
    #     return data.state_of_health[-1] * 100.0

    def delta_total_acdc_efficiency_charge(self) -> dict:
        sim_total_acdc_efficiency_charge = self.__simulation_evaluation.total_acdc_efficiency_charge()
        real_total_acdc_efficiency_charge = self.__real_data_evaluation.total_acdc_efficiency_charge()

        return self.merge_deviations_in_dict(sim_total_acdc_efficiency_charge, real_total_acdc_efficiency_charge)

    def delta_total_acdc_efficiency_discharge(self) -> dict:
        sim_total_acdc_efficiency_discharge = self.__simulation_evaluation.total_acdc_efficiency_discharge()


        return self.merge_deviations_in_dict(sim_total_acdc_efficiency_discharge, real_total_acdc_efficiency_discharge)

    def close(self) -> None:
        self.__log.close()
        super().close()
