from simses.technology.lithium_ion.cell.format.round import RoundCell


class RoundCell21700(RoundCell):

    __DIAMETER: float = 21  # mm
    __LENGTH: float = 70 # mm

    def __init__(self):
        super(RoundCell21700, self).__init__(diameter=self.__DIAMETER, length=self.__LENGTH)
