####################################
# SourcePlacerUI.py
#
# This program puts simulated x-ray sources into a copy of the original galaxy image.
# The output fits file should be used with wavdetect to obtain an estimate of the completeness corrections
#
# You can either enter sources manually one at a time with a specified central point and number of counts
# or you can have sources placed within a grid of specified size. In either case, a region file will also
# be produced to help you find the added sources in the new image.
#
# input: original image fits file
# output: image fits file with added sources, region file of the new sources
####################################

from astropy.io import fits
from astropy.wcs import WCS
import math
import sys
import getopt
from ManualSourcePlacer import ManualSourcePlacer
from GridSourcePlacer import GridSourcePlacer


def is_square(in_num):
    sqrt = math.sqrt(in_num)
    if sqrt != round(sqrt):
        return False
    else:
        return True


def prompts():
    img = raw_input('Enter the name of the galaxy image file (enter for M51): ')
    if img == "":
        img = 'NGC5194-merged-2to7-asca-im-bin1.fits'

    hdulist = fits.open(img)
    wcs = WCS(img)

    cm = raw_input('Enter m value for linear fit of C (enter for default): ') or 0.2349714 #-0.1063655
    cb = raw_input('Enter b value for linear fit of C (enter for default): ') or 0.5901524 #0.57311031
    dm = raw_input('Enter m value for linear fit of D (enter for default): ') or -0.07362884#-0.09808842
    db = raw_input('Enter b value for linear fit of D (enter for default): ') or 1.43515344#1.56873277
    ra = raw_input('Enter on axis ra value (enter for default): ') or 202.50579
    dec = raw_input('Enter on axis dec value (enter for default): ') or 47.186136

    erf_fit_args = [cm, cb, dm, db]
    on_axis_args = [ra, dec]

    while True:
        mode = raw_input('Manual input of sources or grid (m or g): ')

        if mode == 'm':
            sp = ManualSourcePlacer(wcs, hdulist, erf_fit_args, on_axis_args)
            sp.manual_input_sources()
            regions = sp.placed_sources_info
            break

        elif mode == 'g':
            sp = GridSourcePlacer(wcs, hdulist, erf_fit_args, on_axis_args)
            while True:
                num_squares = raw_input(
                    'Enter the total number of squares in the grid (number must be a square number): ')
                try:
                    num_squares = int(num_squares)
                except ValueError:
                    print('That is not an integer!')
                    continue
                if is_square(num_squares) is False:
                    print('That is not a perfect square!')
                    continue
                sqrt = int(math.sqrt(num_squares))
                break
            num_counts = int(raw_input('Enter the number of counts for each source: '))
            sp.place_in_grid(sqrt, num_counts)
            regions = sp.placed_sources_info
            break

        else:
            print('Invalid input!')

    file_name = raw_input('Enter the name of the output file with .fits extension (must not already exist!): ')
    sp.hdulist.writeto(file_name)

    region_file_name = file_name[:-4] + 'reg'
    with open(region_file_name, 'w') as f:
        f.write('# Region file format: DS9 version 4.1\n')
        f.write('image\n')
        f.write("global color=blue\n")
        for region in regions:
            f.write(region.to_reg())

    coords_file_name = file_name[:-4] + 'txt'
    with open(coords_file_name, 'w') as f:
        f.write('RA,DEC\n')
        for region in regions:
            f.write(region.coords_to_text())


def scripting(input_file, output_file, num_squares, num_counts, erf_fit_args, on_axis_args):
    hdulist = fits.open(input_file)
    wcs = WCS(input_file)

    gsp = GridSourcePlacer(wcs, hdulist, erf_fit_args, on_axis_args)

    gsp.place_in_grid(int(math.sqrt(num_squares)), num_counts)

    gsp.hdulist.writeto(output_file)

    region_file_name = output_file[:-4] + 'reg'
    with open(region_file_name, 'w') as f:
        f.write('# Region file format: DS9 version 4.1\n')
        f.write('image\n')
        f.write("global color=blue\n")
        for region in gsp.placed_sources_info:
            f.write(region.to_reg())
        f.close()

    coords_file_name = output_file[:-4] + 'txt'
    with open(coords_file_name, 'w') as f:
        f.write('RA,DEC\n')
        for region in gsp.placed_sources_info:
            f.write(region.coords_to_text())


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o:n:c:", ["cm=", "cb=", "dm=", "db=", "ra=", "dec="])
    except getopt.GetoptError:
        print 'SourcePlacerUI.py -i <inputimagefile> -o <outputfitsfile> -n <ngrid> -c <counts> --cm <m for c fit> --cb <b for c fit> ' \
              '--dm <m for d fit> --db <b for d fit> --ra <ra on axis> --dec <dec on axis>'
        sys.exit()
    if len(argv) == 0:
        prompts()
    else:
        required = {'-i', '-o', '-n', '-c'}
        tags = {pair[0] for pair in opts}

        if (required <= tags) is False and tags != {'-h'}:
            print 'Error: Missing required arguments.'
            sys.exit()

        cm = 0.2349714
        cb = 0.5901524
        dm = -0.07362884
        db = 1.43515344
        ra = 202.50579
        dec = 47.186136

        for opt, arg in opts:
            if opt == '-h':
                print 'SourcePlacerUI.py -i <inputimagefile> -o <outputfitsfile> -n <ngrid> -c <counts> ' \
                      '--cm <m for c fit> --cb <b for c fit> --dm <m for d fit> --db <b for d fit> ' \
                      '--ra <ra on axis> --dec <dec on axis>'
                sys.exit()
            elif opt == '-i':
                in_file = arg
            elif opt == '-o':
                out_file = arg
            elif opt == '-n':
                if is_square(float(arg)) is False:
                    print 'Error: -n input was not a square number.'
                    sys.exit()
                else:
                    num_squares = int(arg)
            elif opt == '-c':
                num_counts = int(arg)
            elif opt == '--cm':
                cm = float(arg)
            elif opt == '--cb':
                cb = float(arg)
            elif opt == '--dm':
                dm = float(arg)
            elif opt == '--db':
                db = float(arg)
            elif opt == '--ra':
                ra = float(arg)
            elif opt == '--dec':
                dec = float(arg)
        scripting(in_file, out_file, num_squares, num_counts, [cm, cb, dm, db], [ra, dec])


if __name__ == "__main__":
    main(sys.argv[1:])
