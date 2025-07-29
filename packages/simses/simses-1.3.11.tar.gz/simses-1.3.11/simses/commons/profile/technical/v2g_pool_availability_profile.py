from simses.commons.profile.file import FileProfile
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.technical.technical import TechnicalProfile

class V2GPoolAvailabilityProfile(TechnicalProfile):
    """
    V2GPoolAvailabilityProfile is a subclass of TechnicalProfile (like SocProfile). The V2G pool availability profile
    should contain a timestep and an availability profile (between 0 and 1). This class is used for V2G simulations
    to estimate the available vehicles of a pool of vehicles. In the V2G simulations, a vehicle pool size of, e.g.,
    80 is assumed. The V2GPoolAvailabilityProfile defines the percentage (in p.u.) of vehicles that are currently
    available.
    The required V2G power is then calculated by dividing the (initially stationary required) power by the number of
    currently available vehicles.
    The profile should be a weekly profile giving the median availability of the vehicles. Depending on the time of the
    week, the current pool size is calculated.

    """

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig):
        super().__init__()
        self.__file: FileProfile = FileProfile(config, profile_config.v2g_pool_availability_profile_file, delimiter=',')

    def next(self, time: float) -> float:
        return self.__file.next(time)


    def close(self):
        self.__file.close()
