import numpy as np
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.plotting.axis import Axis
from simses.analysis.evaluation.plotting.plotly_plotting import PlotlyPlotting
from simses.analysis.evaluation.plotting.plotter import Plotting
from simses.analysis.evaluation.plotting.sankey_diagram import SankeyDiagram
from simses.analysis.evaluation.plotting.sunburst_diagram import SunburstDiagram
from simses.analysis.evaluation.result import EvaluationResult, Description, Unit
from simses.analysis.evaluation.technical.technical_evaluation import TechnicalEvaluation
from simses.analysis.utils import get_positive_values_from, get_sum_for, get_negative_values_from, get_min_for, \
    get_max_for
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.log import Logger
from simses.commons.state.system import SystemState


class SystemTechnicalEvaluation(TechnicalEvaluation):

    __power_title = 'System power'
    __soc_title = 'System SOC'
    __system_thermal_title = 'System thermal parameters'
    __additional_title = 'Additional DC power'
    __power_loss_title = 'Power losses'
    __voltage_title = 'Intermediate circuit voltage'
    __energy_flows_title = 'Energy flows'
    __loss_distribution_title = 'Losses distribution'

    def __init__(self, data: SystemData, config: GeneralAnalysisConfig, path: str):
        super().__init__(data, config)
        self.__log: Logger = Logger(type(self).__name__)
        title_extension: str = ' for system ' + self.get_data().id
        self.__power_title += title_extension
        self.__soc_title += title_extension
        self.__power_loss_title += title_extension
        self.__system_thermal_title += title_extension
        self.__energy_flows_title += title_extension
        self.__additional_title += title_extension
        self.__loss_distribution_title += title_extension
        self.__result_path = path
        self._set_numpy_err_handling()

    def _set_numpy_err_handling(self):
        """Log numpy's `divide by zero` warnings instead of printing"""
        def err_handler(type, flag):
            self.__log.warn("Numpy floating point error (%s), with flag %s" % (type, flag))
        np.seterrcall(err_handler)
        np.seterr(all='call')

    # def __get_initial_capacity_from(self, storage_system_config: StorageSystemConfig) -> float:
    #     capacity: float = 0.0
    #     storage_technologies: dict = storage_system_config.storage_technologies
    #     for storage_system_dc in storage_system_config.storage_systems_dc:
    #         storage_name: str = storage_system_dc[StorageSystemConfig.DC_SYSTEM_STORAGE]
    #         if storage_name in storage_technologies.keys():
    #             capacity += float(storage_technologies[storage_name][StorageSystemConfig.STORAGE_CAPACITY])
    #     return capacity * 1e-3

    def evaluate(self):
        super().evaluate()
        data: SystemData = self.get_data()
        total_dcdc_charge_efficiency: float    = self.total_dcdc_efficiency_charge()
        total_dcdc_discharge_efficiency: float = self.total_dcdc_efficiency_discharge()
        total_dcdc_efficiency = total_dcdc_charge_efficiency * total_dcdc_discharge_efficiency / 100.0
        total_acdc_charge_efficiency: float    = self.total_acdc_efficiency_charge()
        total_acdc_discharge_efficiency: float = self.total_acdc_efficiency_discharge()
        total_acdc_efficiency = total_acdc_charge_efficiency * total_acdc_discharge_efficiency / 100.0
        total_pe_efficiency = total_dcdc_efficiency * total_acdc_efficiency / 100.0

        self.append_result(EvaluationResult(Description.Technical.E_RATE_CHARGING, Unit.ONE_PER_HOUR, self.e_rate_mean_charge()))
        self.append_result(EvaluationResult(Description.Technical.E_RATE_DISCHARGING, Unit.ONE_PER_HOUR, self.e_rate_mean_discharge()))
        self.append_result(EvaluationResult(Description.Technical.DCDC_EFFICIENCY_CHARGE, Unit.PERCENTAGE, total_dcdc_charge_efficiency))
        self.append_result(EvaluationResult(Description.Technical.DCDC_EFFICIENCY_DISCHARGE, Unit.PERCENTAGE, total_dcdc_discharge_efficiency))
        self.append_result(EvaluationResult(Description.Technical.DCDC_EFFICIENCY, Unit.PERCENTAGE, total_dcdc_efficiency))
        self.append_result(EvaluationResult(Description.Technical.ACDC_EFFICIENCY_CHARGE, Unit.PERCENTAGE, total_acdc_charge_efficiency))
        self.append_result(EvaluationResult(Description.Technical.ACDC_EFFICIENCY_DISCHARGE, Unit.PERCENTAGE, total_acdc_discharge_efficiency))
        self.append_result(EvaluationResult(Description.Technical.ACDC_EFFICIENCY, Unit.PERCENTAGE, total_acdc_efficiency))
        self.append_result(EvaluationResult(Description.Technical.PE_EFFICIENCY, Unit.PERCENTAGE, total_pe_efficiency))
        self.append_result(EvaluationResult(Description.Technical.MAX_LOAD_DC_POWER_ADDITIONAL, Unit.WATT, self.max_load_dc_power_additional))
        self.append_result(EvaluationResult(Description.Technical.MAX_GENERATION_DC_POWER_ADDITIONAL, Unit.WATT, self.max_generation_dc_power_additional))
        self.append_result(EvaluationResult(Description.Technical.SYSTEM_TEMPORAL_UTILIZATION, Unit.NONE, self.system_temporal_utilization()))
        # self.append_time_series(SystemState.DC_POWER_ADDITIONAL, data.dc_power_additional)
        # self.append_time_series(SystemState.DC_POWER_STORAGE, data.dc_power_storage)
        # self.append_time_series(SystemState.SOC, data.soc)
        self.print_results()

    def plot(self) -> None:
        self.__power_plotting()
        self.__soc_plotting()
        self.__power_loss_plotting()
        self.__system_thermal_plotting()
        # self.__voltage_plotting()
        self.__additional_dc_power_plotting()
        self.__energy_flows_plotting()
        self.__loss_distribution_plotting()

    def __soc_plotting(self):
        data: SystemData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=self.__soc_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=SystemState.TIME)
        yaxis: [Axis] = [Axis(data.soc, label=SystemState.SOC, color=PlotlyPlotting.Color.SOC_BLUE)]
        plot.lines(xaxis, yaxis)
        plot.histogram(xaxis=xaxis, yaxis=yaxis)
        self.extend_figures(plot.get_figures())

    def __voltage_plotting(self):
        data: SystemData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=self.__voltage_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=SystemState.TIME)
        yaxis: [Axis] = [Axis(data.dc_voltage, label=SystemState.DC_VOLTAGE_CIRCUIT, color=PlotlyPlotting.Color.SOC_BLUE)]
        plot.lines(xaxis, yaxis)
        plot.histogram(xaxis=xaxis, yaxis=yaxis)
        self.extend_figures(plot.get_figures())

    def __power_loss_plotting(self):
        data: SystemData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=self.__power_loss_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=SystemState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.pe_losses, label=SystemState.PE_LOSSES, color=PlotlyPlotting.Color.RED,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.dc_power_loss, label=SystemState.DC_POWER_LOSS, color=PlotlyPlotting.Color.HEAT_ORANGE,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.storage_technology_loss_power, label=SystemState.STORAGE_POWER_LOSS, color=PlotlyPlotting.Color.BLACK,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.aux_power, label=SystemState.AUX_LOSSES,
                          color=PlotlyPlotting.Color.BLUE, linestyle=PlotlyPlotting.Linestyle.SOLID))
        plot.lines(xaxis=xaxis, yaxis=yaxis)
        self.extend_figures(plot.get_figures())

    def __additional_dc_power_plotting(self):
        data: SystemData = self.get_data()
        if sum(abs(data.dc_power_additional)) > 0.0:
            plot: Plotting = PlotlyPlotting(title=self.__additional_title, path=self.__result_path)
            xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=SystemState.TIME)
            yaxis: [Axis] = [Axis(data.dc_power_additional, label=SystemState.DC_POWER_ADDITIONAL)]
            plot.lines(xaxis, yaxis)
            self.extend_figures(plot.get_figures())

    def __power_plotting(self):
        data: SystemData = self.get_data()
        plot: Plotting = PlotlyPlotting(title=self.__power_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=SystemState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data.dc_power_storage, label=SystemState.DC_POWER_STORAGE,
                          color=PlotlyPlotting.Color.DC_POWER_GREEN,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data.power, label=SystemState.AC_POWER_DELIVERED,
                          color=PlotlyPlotting.Color.AC_POWER_BLUE,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data.dc_power, label=SystemState.DC_POWER_INTERMEDIATE_CIRCUIT,
                          color=PlotlyPlotting.Color.RED,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data.ac_power_target, label=SystemState.AC_POWER,
                          color=PlotlyPlotting.Color.GREEN,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        plot.lines(xaxis=xaxis, yaxis=yaxis)
        plot.histogram(xaxis=xaxis, yaxis=yaxis)
        self.extend_figures(plot.get_figures())

    def __system_thermal_plotting(self):

        data: SystemData = self.get_data()
        if abs(sum(data.hvac_thermal_power)) > 1:  # HVAC power only present in scenarios with housing and solar irradiation
            plot: Plotting = PlotlyPlotting(title=self.__system_thermal_title, path=self.__result_path)
            xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=SystemState.TIME)
            yaxis: [Axis] = list()

            yaxis.append(Axis(data=data.solar_thermal_load, label=SystemState.SOLAR_THERMAL_LOAD,
                              color=PlotlyPlotting.Color.POWER_YELLOW, linestyle=PlotlyPlotting.Linestyle.SOLID))
            yaxis.append(Axis(data=-1*data.hvac_thermal_power, label=SystemState.HVAC_THERMAL_POWER, color=PlotlyPlotting.Color.BRIGHT_BLUE,
                              linestyle=PlotlyPlotting.Linestyle.SOLID))
            plot.subplots(xaxis=xaxis, yaxis=yaxis)
            self.extend_figures(plot.get_figures())

        plot3: Plotting = PlotlyPlotting(title=self.__system_thermal_title, path=self.__result_path)
        xaxis: Axis = Axis(data=Plotting.format_time(data.time), label=SystemState.TIME)
        yaxis: [Axis] = list()
        yaxis.append(Axis(data=data.ambient_temperature, label=SystemState.AMBIENT_TEMPERATURE,
                          color=PlotlyPlotting.Color.BRIGHT_GREEN, linestyle=PlotlyPlotting.Linestyle.SOLID))
        if sum(data.ol_temperature) > 1:
            yaxis.append(Axis(data=data.ol_temperature, label=SystemState.OL_TEMPERATURE, color=PlotlyPlotting.Color.YELLOW,
                              linestyle=PlotlyPlotting.Linestyle.SOLID))
            yaxis.append(Axis(data=data.il_temperature, label=SystemState.IL_TEMPERATURE, color=PlotlyPlotting.Color.GREY,
                              linestyle=PlotlyPlotting.Linestyle.SOLID))
        yaxis.append(Axis(data=data.temperature, label=SystemState.TEMPERATURE, color=PlotlyPlotting.Color.TEMPERATURE_RED,
                          linestyle=PlotlyPlotting.Linestyle.SOLID))
        plot3.lines(xaxis=xaxis, yaxis=yaxis)
        self.extend_figures(plot3.get_figures())

    def __energy_flows_plotting(self):
        data: SystemData = self.get_data()
        sankey_diagram: SankeyDiagram = SankeyDiagram(data, title=self.__energy_flows_title, path=self.__result_path)
        node_links: dict = sankey_diagram.create_node_links()
        plot: Plotting = PlotlyPlotting(self.__energy_flows_title, self.__result_path)
        plot.sankey_diagram(node_links)
        self.extend_figures(plot.get_figures())

    def __loss_distribution_plotting(self):
        data: SystemData = self.get_data()
        sunburst_diagram: SunburstDiagram = SunburstDiagram(data, title=self.__loss_distribution_title, path=self.__result_path)
        diagram_parameters: dict = sunburst_diagram.create_parameters()
        plot: Plotting = PlotlyPlotting(self.__loss_distribution_title, self.__result_path)
        plot.sunburst_diagram(diagram_parameters)
        self.extend_figures(plot.get_figures())

    @property
    def max_load_dc_power_additional(self) -> float:
        data: SystemData = self.get_data()
        dc_power = min(0.0, get_min_for(data.dc_power_additional))
        return abs(dc_power)

    @property
    def max_generation_dc_power_additional(self) -> float:
        data: SystemData = self.get_data()
        dc_power = max(0.0, get_max_for(data.dc_power_additional))
        return abs(dc_power)


    def __total_charge_efficiency(self, power_in: np.ndarray, power_out: np.ndarray) -> float:
        """
        Calculates the total charge efficiency.

        Parameters
        ----------
        power_in: np.ndarray
            power coming into the converter
        power_out: np.ndarray
            power coming out of the converter

        Returns
        -------
        total_charge_efficiency: float
        """
        total_power_in = power_in[power_in > 0].sum()
        total_power_out = power_out[power_out > 0].sum()
        return 100.0 * (total_power_out / total_power_in)

    def __total_discharge_efficiency(self, power_in: np.ndarray, power_out: np.ndarray) -> float:
        """
        Calculates the total discharge efficiency

        Parameters
        ----------
        power_in: np.ndarray
            power coming into the converter
        power_out: np.ndarray
            power coming out of the converter

        Returns
        -------
        total_discharge_efficiency: float
        """
        total_power_in = power_in[power_in < 0].sum()
        total_power_out = power_out[power_out < 0].sum()
        return 100.0 * (total_power_out / total_power_in)

    def total_dcdc_efficiency_charge(self) -> float:
        data: SystemData = self.get_data()
        dc_power_intermediate_circuit = data.dc_power + data.dc_power_additional
        return self.__total_charge_efficiency(dc_power_intermediate_circuit, data.dc_power_storage)

    def total_dcdc_efficiency_discharge(self) -> float:
        data: SystemData = self.get_data()
        dc_power_intermediate_circuit = data.dc_power + data.dc_power_additional
        return self.__total_discharge_efficiency(data.dc_power_storage, dc_power_intermediate_circuit)

    def total_acdc_efficiency_charge(self) -> float:
        data: SystemData = self.get_data()
        return self.__total_charge_efficiency(data.ac_pe_power, data.dc_power)

    def total_acdc_efficiency_discharge(self) -> float:
        data: SystemData = self.get_data()
        return self.__total_discharge_efficiency(data.dc_power, data.ac_pe_power)

    def system_temporal_utilization(self) -> float:
        """
        calculates and returns system temporal utilization in p.u.
        :return: system temporal utilization as float
        """
        data: SystemData = self.get_data()
        ac_power: np.ndarray = data.power
        t_simulation = len(ac_power)
        t_operation = len(np.where(ac_power != 0)[0])
        return t_operation/t_simulation

    @staticmethod
    def __contains_only_nan(data: np.ndarray) -> bool:
        """
        If data array contains only NaN, method returns True; False otherwise.

        Parameters
        ----------
        data :

        Returns
        -------

        """
        return len(data) == 0 or np.isnan(data).all()

    def e_rate_mean_charge(self) -> float:
        """
        Calculates the average e-rate while charging
        E-rate is calculated by avg. power (W) divided by energy (Wh)

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            mean e-rate when charging
        """

        data: SystemData = self.get_data()
        battery_energy = 1000 * data.initial_capacity  # in Wh
        charge_power_mean = np.mean(data.power[data.power > 0])
        e_rate_charging = charge_power_mean / battery_energy  # based on power and energy instead of current and capacity

        return e_rate_charging

    def e_rate_mean_discharge(self) -> float:
        """
        Calculates the average e-rate while discharging.
        E-rate is calculated by avg. power (W) divided by energy (Wh)

        Parameters
        ----------
            data : simulation results

        Returns
        -------
        float:
            mean e-rate when discharging
        """

        data: SystemData = self.get_data()
        battery_energy = 1000 * data.initial_capacity  # in Wh
        discharge_power_mean = np.mean(data.power[data.power < 0])
        e_rate_discharging = -discharge_power_mean / battery_energy  # based on power and energy instead of current and capacity

        return e_rate_discharging

    def close(self) -> None:
        self.__log.close()
        super().close()
