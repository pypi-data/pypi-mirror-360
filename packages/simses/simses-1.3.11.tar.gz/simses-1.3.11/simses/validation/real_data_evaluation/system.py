from simses.commons.log import Logger
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.config.validation.general import GeneralValidationConfig

from simses.analysis.evaluation.result import EvaluationResult, Description, Unit

from simses.validation.validation_data.real_system import RealSystemData
from simses.validation.real_data_evaluation.technical_evaluation import RealDataTechnicalEvaluation


class RealDataSystemTechnicalEvaluation(RealDataTechnicalEvaluation):

    def __init__(self, data: RealSystemData, validation_config: GeneralValidationConfig, analysis_config: GeneralAnalysisConfig):
        super().__init__(data, validation_config, analysis_config)
        self.__log: Logger = Logger(type(self).__name__)

    def evaluate(self):
        super().evaluate()
        total_dcdc_charge_efficiency: float = self.total_dcdc_efficiency_charge()
        total_dcdc_discharge_efficiency: float = self.total_dcdc_efficiency_discharge()
        total_dcdc_efficiency = total_dcdc_charge_efficiency * total_dcdc_discharge_efficiency / 100.0
        total_acdc_charge_efficiency: float = self.total_acdc_efficiency_charge()
        total_acdc_discharge_efficiency: float = self.total_acdc_efficiency_discharge()
        total_acdc_efficiency = total_acdc_charge_efficiency * total_acdc_discharge_efficiency / 100.0
        total_pe_efficiency = total_dcdc_efficiency * total_acdc_efficiency / 100.0

        self.append_result(EvaluationResult(Description.Technical.DCDC_EFFICIENCY_CHARGE, Unit.PERCENTAGE,
                                            total_dcdc_charge_efficiency))
        self.append_result(EvaluationResult(Description.Technical.DCDC_EFFICIENCY_DISCHARGE, Unit.PERCENTAGE,
                                            total_dcdc_discharge_efficiency))
        self.append_result(
            EvaluationResult(Description.Technical.DCDC_EFFICIENCY, Unit.PERCENTAGE, total_dcdc_efficiency))
        self.append_result(EvaluationResult(Description.Technical.ACDC_EFFICIENCY_CHARGE, Unit.PERCENTAGE,
                                            total_acdc_charge_efficiency))
        self.append_result(EvaluationResult(Description.Technical.ACDC_EFFICIENCY_DISCHARGE, Unit.PERCENTAGE,
                                            total_acdc_discharge_efficiency))
        self.append_result(
            EvaluationResult(Description.Technical.ACDC_EFFICIENCY, Unit.PERCENTAGE, total_acdc_efficiency))

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


