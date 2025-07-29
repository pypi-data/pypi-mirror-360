from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.equivalent_circuit_model.equivalent_circuit import EquivalentCircuitModel


class RintModel(EquivalentCircuitModel):

    __ACCURACY: float = 1e-7

    def __init__(self, cell_type: CellType):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__cell_type: CellType = cell_type

    def update(self, time: float, battery_state: LithiumIonState) -> None:
        bs: LithiumIonState = battery_state

        # get all losses
        coulomb_eff = self.__cell_type.get_coulomb_efficiency(bs)
        self_discharge_losses_wh = self.__cell_type.get_self_discharge_rate(bs) * (time - bs.time)
        hysteresis_losses_wh = abs(0.5 * bs.voltage_hysteresis * bs.current * (time - bs.time) / 3600.0)
        coulomb_efficiency_losses_wh = bs.current * bs.voltage_open_circuit * (time - bs.time) / 3600.0 * (1-coulomb_eff)
        rint_losses_wh = bs.current**2 *bs.internal_resistance * (time - bs.time) / 3600
        bs.power_loss = (self_discharge_losses_wh + hysteresis_losses_wh + coulomb_efficiency_losses_wh
                         + rint_losses_wh) * 3600 / (time - bs.time)  # total power losses in W

        # calculate new state variables: soc, ocv, hysteresis voltage and internal resistance
        self.__update_soc(time, bs, coulomb_efficiency_losses_wh, self_discharge_losses_wh, hysteresis_losses_wh)
        ocv: float = self.__cell_type.get_open_circuit_voltage(bs)  # V
        bs.voltage_open_circuit = ocv

        hystv: float = self.__cell_type.get_hysteresis_voltage(bs) # V
        bs.voltage_hysteresis = hystv

        rint = self.__cell_type.get_internal_resistance(bs) * (1 + bs.resistance_increase)
        bs.internal_resistance = rint

    def __update_soc(self, time: float, bs: LithiumIonState, coulomb_efficiency_losses_wh: float,
                     self_discharge_losses_wh: float, hysteresis_losses_wh: float) -> None:
        # Wh counting
        delta_energy = bs.current * bs.voltage_open_circuit * (time - bs.time) / 3600.0
        # Rint losses already considered
        bs.soe += delta_energy - coulomb_efficiency_losses_wh - self_discharge_losses_wh - hysteresis_losses_wh

        # ignore hysteresis voltage losses on last timestep during discharge, otherwise negative soe
        if bs.soe < 0:
            bs.soe += hysteresis_losses_wh

        bs.soc = bs.soe / bs.capacity

        # assuming rounding errors close to 0 or 1
        if abs(bs.soc) < self.__ACCURACY:
            self.__log.warn('SOC was tried to be set to a value of ' + str(bs.soc) + ' but adjusted to 0.0.')
            bs.soc = 0.0
        if abs(bs.soc - 1.0) < self.__ACCURACY:
            self.__log.warn('SOC was tried to be set to a value of ' + str(bs.soc) + ' but adjusted to 1.0.')
            bs.soc = 1.0

    def __get_all_losses(self, time: float ):
        pass


    def close(self) -> None:
        self.__log.close()
