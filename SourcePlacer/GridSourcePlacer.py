####################################
# GridSourcePlacer.py
#
# Subclass of SourcePlacer which places sources in a grid pattern.
####################################

from SourcePlacer import SourcePlacer
from random import uniform


class SquareError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GridSourcePlacer(SourcePlacer):
    def __init__(self, wcs, hdulist, erf_fit_args, on_axis_args):
        SourcePlacer.__init__(self, wcs, hdulist, erf_fit_args, on_axis_args)

    def place_in_grid(self, sqrt, num_counts):
        x_step = self.max_x / sqrt
        y_step = self.max_y / sqrt

        # for i in range(0, sqrt, x_step)
        for i in range(sqrt):
            for j in range(sqrt):
                # rand_x = uniform(i , i + x_step)
                rand_x = uniform(j * x_step, (j + 1) * x_step)
                rand_y = uniform(i * y_step, (i + 1) * y_step)
                # rand_x = (j*x_step + (j+1)*x_step)/2
                # rand_y = (i*y_step + (i+1)*y_step)/2
                self.place_source(num_counts, rand_x, rand_y)
