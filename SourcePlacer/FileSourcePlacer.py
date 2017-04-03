####################################
# FileSourcePlacer.py
#
# Subclass of SourcePlacer which reads in the information needed to place a source
# from a file specified when creating the FileSourcePlacer.
#
# Note: this SourcePlacer is only handles the information in the file related to the
# sources' position and size. You could have more information within the file (such as
# the name of the image file, output fits file, or various arguments related to the image)
# but this subclass is not designed to handle them. If you would like this information to
# also be contained in the file, put it before the source info and when invoking the
# place_sources_from_file function indicate how many lines in the file should be skipped.
#
# A FileSourcePlacer assumes the file has the following format:
# numcounts1,x1,y1
# numcounts2,x2,y2
# etc.
####################################

from SourcePlacer import SourcePlacer
from astropy.io import fits
from astropy.wcs import WCS

class FileSourcePlacer(SourcePlacer):
    def __init__(self, wcs, hdulist, erf_fit_args, on_axis_args):
        SourcePlacer.__init__(self, wcs, hdulist, erf_fit_args, on_axis_args)

    def place_sources_from_file(self, filename, lines_to_skip=0):
        with open(filename, 'r') as f:
            for skip in range(lines_to_skip):
                next(f)

            for line in f:
                num_counts,x,y = line.split(",")
                self.place_source(int(num_counts),float(x),float(y))


def test():
    input_file = 'test.txt'
    image_file = 'NGC5194-merged-2to7-asca-im-bin1.fits'
    output_file = 'test.fits'

    hdulist = fits.open(image_file)
    wcs = WCS(image_file)

    cm = -0.11427239
    cb = 0.58578096
    dm = -0.07072029
    db = 1.353355987
    ra = 202.50579
    dec = 47.186136

    erg_fit_args = [cm, cb, dm, db]
    on_axis_args = [ra, dec]

    fsp = FileSourcePlacer(wcs, hdulist, erg_fit_args, on_axis_args)
    fsp.place_sources_from_file(input_file)

    fsp.hdulist.writeto(output_file)

if __name__ == "__main__":
    test()
