####################################
# ErfHandler.py
#
# Class that handles all of the functions and calculations related to
# the erf fit from photometry measurements. Note that the function used to
# those psf curves was of the for y = erf(c x^d) where x is a radius in pix
# and y is a fraction. C and D is constant that depend on the source's
# degree off axis.
####################################
import scipy.special


class ErfHandler:
    def __init__(self, erf_fit_args):
        self._erf_fit_args = erf_fit_args

    def get_local_cd(self, degree_off):
        c_fit_line = self.tanhFitCs(*self._erf_fit_args[0:2])
        d_fit_line = self.linear(*self._erf_fit_args[2:])

        local_c = c_fit_line(degree_off)
        local_d = d_fit_line(degree_off)

        return local_c, local_d

    # Inverse of determined erf of the form y = erf(Cx^D)
    def make_erf_inverse(self, c, d):
        return lambda y: (scipy.special.erfinv(y) / c) ** (1 / d)

    def linear(self, m, b):
        return lambda x: m * x + b

    def tanhFitCs(self, m, b):
        return lambda x: b * scipy.tanh(-m * x) + b
