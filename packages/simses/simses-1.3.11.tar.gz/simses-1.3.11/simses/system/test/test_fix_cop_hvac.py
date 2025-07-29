from configparser import ConfigParser
import pytest
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.system.auxiliary.heating_ventilation_air_conditioning.fix_cop_hvac import \
    FixCOPHeatingVentilationAirConditioning
from random import randrange


class TestFixCOPHeatingVentilationAirConditioning:

    # Ensure if path from simulation.defaults.ini to ambient temperature model works
    hvac_model_config: ConfigParser = ConfigParser()
    hvac_model_config.add_section('STORAGE_SYSTEM')
    hvac_model_config.set('STORAGE_SYSTEM', 'HVAC', 'constant_hvac,FixCOPHeatingVentilationAirConditioning,5000,25')
    storage_system_config = StorageSystemConfig(hvac_model_config)
    hvac = 'constant_hvac'
    hvac_model = storage_system_config.hvac[hvac][StorageSystemConfig.HVAC_TYPE]
    hvac_configuration = storage_system_config.hvac[hvac]

    set_point_deviation = 20  # °C
    air_mass = 100  # in kg
    air_specific_heat = 1006  # J/kgK
    temperature = 295  # K
    temperature_timestep = 60

    air_pressure = 1 * 10 ** 5  # Pa, change if container is pressurized
    universal_gas_constant = 8.314  # J/kgK
    molecular_weight_air = 28.965 * 10 ** -3  # kg/mol
    individual_gas_constant = universal_gas_constant / molecular_weight_air  # J/kgK
    air_density = air_pressure / (individual_gas_constant * temperature)

    max_thermal_power: int = int(storage_system_config.hvac[hvac][StorageSystemConfig.HVAC_POWER])  # in W
    set_point_temperature: int = int(storage_system_config.hvac[hvac][StorageSystemConfig.HVAC_TEMPERATURE_SETPOINT])  # in °C

    internal_air_temps = list(range(set_point_temperature - set_point_deviation, set_point_temperature + set_point_deviation, 1))  # K
    ambient_temps = list(range(260, 320, 1))  # K

    test_values = list()
    for x in internal_air_temps:
        for y in ambient_temps:
            test_values.append((x + 273.15, y))

    def create_model(self):
        if self.hvac_model == FixCOPHeatingVentilationAirConditioning.__name__:
            return FixCOPHeatingVentilationAirConditioning(self.hvac_configuration)

    @pytest.mark.parametrize('internal_air_temperature, ambient_air_temp', test_values)
    def test_run_air_conditioning(self, internal_air_temperature, ambient_air_temp):
        uut: FixCOPHeatingVentilationAirConditioning = self.create_model()
        uut.update_air_parameters(self.air_mass, self.air_specific_heat, self.air_density)  # Dummy value for mass of air

        uut.run_air_conditioning([internal_air_temperature], self.temperature_timestep, ambient_air_temp)

        thermal_power = uut.get_thermal_power()
        tms_temperature_dead_band = uut.get_temperature_dead_band()

        set_point_temperature = self.set_point_temperature + 273.15  # K

        if internal_air_temperature > set_point_temperature + tms_temperature_dead_band:
            # Cooling
            assert thermal_power >= 0
            if internal_air_temperature < ambient_air_temp:
                # Fresh air cooling not possible
                assert abs(thermal_power) <= self.max_thermal_power
        elif internal_air_temperature < set_point_temperature - tms_temperature_dead_band:
            # Heating
            assert thermal_power < 0
            if internal_air_temperature > ambient_air_temp:
                # Fresh air heating not possible
                assert abs(thermal_power) <= self.max_thermal_power
        else:
            assert thermal_power == 0
