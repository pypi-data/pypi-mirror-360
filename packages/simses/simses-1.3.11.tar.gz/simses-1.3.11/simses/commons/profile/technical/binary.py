from simses.commons.profile.file import FileProfile
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.technical.technical import TechnicalProfile
from copy import copy
import numpy as np

class BinaryProfile(TechnicalProfile):
    """
    BinaryProfile is a subclass of TechnicalProfile (like SocProfile). The binary profile should contain a timestep and
    a binary profile (0 or 1). This class is used for temporary unavailable storage systems, e.g. mobile applications
    like electric vehicles. Here zeros indicate that the car is on the road respectively not "at home" and ones indicate
    that the car is "at home" and could be charged.
    """

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig):
        super().__init__()
        self.__file: FileProfile = FileProfile(config, profile_config.binary_profile_file, delimiter=',')
        self.__file_copy: FileProfile = FileProfile(config, profile_config.binary_profile_file, delimiter=',')


    def next(self, time: float) -> float:
        return self.__file.next(time)


    def next_change_in_binary(self, time: float, current_binary: bool) -> float:

        time_copy = copy(time)
        current_value = current_binary
        while bool(np.ceil(current_value)) == current_binary and time_copy < self.__file_copy._FileProfile__end:
            # maximum until end of file
            time_copy += 1
            current_value = self.__file_copy.next(time_copy)

        return time_copy


    def close(self):
        self.__file.close()
        self.__file_copy.close()
