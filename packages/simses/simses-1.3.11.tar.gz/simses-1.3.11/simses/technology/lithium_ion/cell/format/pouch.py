
from simses.technology.lithium_ion.cell.format.abstract import CellFormat


class PouchCell(CellFormat):

    def __init__(self, height: float, width: float, length: float):
        super(PouchCell, self).__init__()
        self.__volume = height * width * length  # m3
        self.__surface_area = 2.0 * (length * height + length * width + width * height)  # m2

    def get_volume(self) -> float:
        return self.__volume

    def get_surface_area(self) -> float:
        return self.__surface_area
