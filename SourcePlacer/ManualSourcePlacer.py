####################################
# ManualSourcePlacer.py
#
# Subclass of SourcePlacer which utuilizes user input to determine
# where sources should be placed one at a time.
####################################

from SourcePlacer import SourcePlacer


class ManualSourcePlacer(SourcePlacer):
    def __init__(self, wcs, hdulist, erf_fit_args, on_axis_args):
        SourcePlacer.__init__(self, wcs, hdulist, erf_fit_args, on_axis_args)

    def manual_input_sources(self):
        while True:
            x = raw_input('Enter the x position (pixel with 0,0 origin) of the source (q to quit): ')
            if x == 'q':
                break
            try:
                x = float(x)
            except ValueError:
                print('That is not a number!')
                continue
            if x < 0 or x >= self.max_x:
                print('That value is not within the image!')
                continue

            while True:
                y = raw_input('Enter the y position (pixel with 0,0 origin) of the source: ')
                try:
                    y = float(y)
                except ValueError:
                    print('That is not a number!')
                    continue
                if y < 0 or y >= self.max_y:
                    print('That value is not within the image!')
                    continue
                else:
                    break

            while True:
                num_counts = raw_input('Enter the number of counts for the source: ')
                try:
                    num_counts = int(num_counts)
                except ValueError:
                    print('That is not a integer!')
                    continue
                if num_counts < 0:
                    print('Invalid input!')
                    continue
                else:
                    break
            self.place_source(num_counts, x, y)
