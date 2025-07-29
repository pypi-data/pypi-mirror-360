import os
from configparser import ConfigParser
from datetime import datetime, timezone
import pytest
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.utils.utilities import remove_file
from simses.system.thermal.ambient.location_temperature import LocationAmbientTemperature
from simses.system.thermal.ambient.user_battery_temperature import UserBatteryTemperatureProfile

DELIMITER: str = ','
HEADER: str = '# Unit: C'
START: int = 0
END: int = 60
STEP: int = 1


def create_file(value, string:str = '1') -> str:
    filename = string + 'mockup_ambient_temperature_profile.csv'
    path: str = os.path.join(os.path.dirname(__file__), filename)
    with open(path, mode='w') as file:
        file.write(HEADER + '\n')
        # add inputs
        tstmp = START
        while tstmp <= END:
            file.write(str(tstmp) + DELIMITER + str(value) + '\n')
            tstmp += STEP
    return path


def create_general_config() -> GeneralSimulationConfig:
    conf: ConfigParser = ConfigParser()
    conf.add_section(GeneralSimulationConfig.SECTION)
    date = datetime.fromtimestamp(START, timezone.utc)
    conf.set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.START, date.strftime("%Y-%m-%d %H:%M:%S"))
    date = datetime.fromtimestamp(END, timezone.utc)
    conf.set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.END, date.strftime("%Y-%m-%d %H:%M:%S"))
    conf.set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.TIME_STEP, str(STEP))
    return GeneralSimulationConfig(conf)


def create_profile_config(filename: str) -> ProfileConfig:
    conf: ConfigParser = ConfigParser()
    conf.add_section(ProfileConfig.SECTION)
    conf.set(ProfileConfig.SECTION, ProfileConfig.THERMAL_PROFILE_DIR, os.path.dirname(filename))
    conf.set(ProfileConfig.SECTION, ProfileConfig.AMBIENT_TEMPERATURE_PROFILE, os.path.basename(filename))
    return ProfileConfig(conf)


def create_profile_config_2(filename: str) -> ProfileConfig:
    conf: ConfigParser = ConfigParser()
    conf.add_section(ProfileConfig.SECTION)
    conf.set(ProfileConfig.SECTION, ProfileConfig.THERMAL_PROFILE_DIR, os.path.dirname(filename))
    conf.set(ProfileConfig.SECTION, ProfileConfig.BATTERY_TEMPERATURE_PROFILE, os.path.basename(filename))
    return ProfileConfig(conf)


@pytest.fixture(scope='function')
def uut(ambient_temperature):
    filename = create_file(ambient_temperature)
    uut = LocationAmbientTemperature(create_profile_config(filename), create_general_config())
    yield uut
    uut.close()
    remove_file(filename)


@pytest.fixture(scope='function')
def uut2(ambient_temperature):
    filename = create_file(ambient_temperature, string='2')
    uut2 = UserBatteryTemperatureProfile(create_profile_config_2(filename), create_general_config())
    yield uut2
    uut2.close()
    remove_file(filename)


@pytest.mark.parametrize('ambient_temperature, time_factor, result',
                         [
                             (0, 1, 0),
                             (0, 1, 0),
                             (1, 1, 1),
                             (2, 1, 2),
                             (6, 2, 6),
                             (1, 5, 1),
                             (-1, 5, -1),
                             (-15, 4, -15),
                             (-25,10,-25)
                         ]
                         )
def test_get_temperature(time_factor, result, uut, uut2):
    tstmp = START
    while tstmp < END:
        assert abs(uut.get_temperature(tstmp) - (result + 273.15)) <= 1e-10
        assert abs(uut2.get_temperature(tstmp) - (result + 273.15)) <= 1e-10
        tstmp += STEP * time_factor