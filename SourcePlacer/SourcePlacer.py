####################################
# SourcePlacer.py
#
# This class handles the actual placement of x-ray sources in an image.
# Note that is has access to the hdulist in order to manipulate the data which
# can be accessed when done adding sources but it does not actually read from
# or write to the file. A source placer also has a list containing all of the region
# info for every source it added to the image.
####################################

from random import uniform
import math
from ErfHandler import ErfHandler


class SingleSourceRegionInfo:
    def __init__(self, x, y, ra, dec, r90):
        self.central_x = x
        self.central_y = y
        self.central_ra = ra
        self.central_dec = dec
        self.radius = r90

    def to_reg(self):
        return "circle({},{},{})\n".format(self.central_x, self.central_y, self.radius)

    def coords_to_text(self):
        return '{},{}\n'.format(self.central_ra, self.central_dec)


class SourcePlacer:
    def __init__(self, wcs, hdulist, erf_fit_args, on_axis_args):
        self.__wcs = wcs

        self.hdulist = hdulist
        hdu = self.hdulist[0]
        self._data = hdu.data

        self.max_x = len(self._data[0]) - 1
        self.max_y = len(self._data) - 1

        self.__erf_fit_args = erf_fit_args
        self.__erf_handler = ErfHandler(erf_fit_args)

        self.__on_axis_args = on_axis_args

        self.placed_sources_info = list()

    def place_source(self, num_counts, x, y):
        ra, dec = self.__wcs.all_pix2world(x, y, 0)
        degree_off = self.__calc_off_axis(ra, dec)
        if degree_off > 5:
            print degree_off
        local_c, local_d = self.__erf_handler.get_local_cd(degree_off)
        erf_inverse = self.__erf_handler.make_erf_inverse(local_c, local_d)

        for count in range(num_counts):
            self.__place_rand_count(x, y, erf_inverse)

        r90 = self.__get_r90(erf_inverse)

        self.placed_sources_info.append(SingleSourceRegionInfo(x + 1, y + 1, ra, dec, r90))

    def __place_rand_count(self, central_x, central_y, erf_inverse):
        radius = self.__rand_radius(erf_inverse)
        angle = uniform(0, 2 * math.pi)
        # print "Radius: ", radius
        # print "Angle: ", angle

        shift_x = radius * math.cos(angle)
        shift_y = radius * math.sin(angle)

        place_x = int(round(central_x + shift_x))
        place_y = int(round(central_y + shift_y))

        if 0 <= place_x <= self.max_x and 0 <= place_y <= self.max_y:
            self._data[place_y][place_x] += 1

    def __calc_off_axis(self, ra, dec):
        return math.sqrt(((ra - self.__on_axis_args[0]) * math.cos(self.__on_axis_args[1] * math.pi / 180)) ** 2 + (dec - self.__on_axis_args[1]) ** 2) * 60

    # This random radius is calculated from a random percent which is fed into the inverse erf equation
    # to get the corresponding radius.
    def __rand_radius(self, erf_inverse):
        rand_percent = uniform(0, 1)
        # print "Percent: ", rand_percent

        radius = erf_inverse(rand_percent)

        return radius

    def __get_r90(self, erf_inverse):
        radius = erf_inverse(0.9)

        return radius
