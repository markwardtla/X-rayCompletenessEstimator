from astropy.io import fits
from astropy.wcs import WCS
from photutils import CircularAperture
from photutils import CircularAnnulus
from photutils import aperture_photometry
import matplotlib.pyplot as plt
import matplotlib.colors as cls
import matplotlib.cm as cm
from random import uniform
from random import randint
import math
import numpy as np
from scipy.optimize import curve_fit
import scipy


def erfFit(x, c, d):
    return scipy.special.erf(c * x ** d)


def erfFitInv(y, c, d):
    return (scipy.special.erfinv(y) / c) ** (1 / d)


# y = 0.5tanh(c(x+d))+0.5
def tanhFit(x, c, d):
    return scipy.tanh(c * x) + scipy.tanh(d * x)


def tanhFitInv(y, c, d):
    return (scipy.arctanh(y) / c)


def tanhFitCs(x, m, b):
    return b * scipy.tanh(-m * x) + b


def tanhFitCsInv(y, m, b):
    return scipy.arctanh(y / b - 1) / -m


def linear(x, m, b):
    return m * x + b


def invLinear(y, m, b):
    return (y - b) / m


def createFitLine(maxnum, f, popt):
    print 'popt in fit:', popt
    fitYs = list()
    fitXs = np.linspace(0, maxnum, num=100)
    for x in fitXs:
        fitYs.append(f(x, *popt))
    return fitXs, fitYs


def calcOffAxis(ra, dec):
    return math.sqrt(((ra - 202.50579) * math.cos(47.186136 * math.pi / 180)) ** 2 + (dec - 47.186136) ** 2) * 60


def circleApp(x, y, r, img_data):
    numAps = 20;
    maxR = 1.5;

    myPhot = list()
    myRs = list()
    myCounts = list()
    myCountsNoBack = list()
    positions = [(x, y)]
    # print positions

    print r
    print(maxR * r)
    myBackAp = CircularAnnulus(positions, r_in=maxR * r, r_out=(maxR + 0.5) * r)  # / numAps)
    myBackPhot = aperture_photometry(img_data, myBackAp)
    print myBackPhot['aperture_sum'][0]
    myBackRate = myBackPhot['aperture_sum'][
                     0] / myBackAp.area()  # (math.pi * (((maxR + 0.5) * r) ** 2 - (maxR * r) ** 2))
    print myBackRate

    for j in range(numAps):
        curR = maxR * r * (j + 1) / numAps
        aperture = CircularAperture(positions, r=curR)
        myRs.append(curR)  # maxR*(j+1.0)/numAps
        myPhot.append(aperture_photometry(img_data, aperture, method="exact"))
        tmp = myPhot[j]

        myCounts.append(tmp['aperture_sum'][0] - (myBackRate * aperture.area()))  # math.pi * (curR) ** 2))
        myCountsNoBack.append(tmp['aperture_sum'][0])

    yerr = np.sqrt(myCountsNoBack) / myCountsNoBack[numAps - 1]  # don't use subtract background

    return myRs, myCountsNoBack, yerr

def main():
    numAps = 20;
    maxR = 1.5;
    f = open('NGC5194-hardband-good-sources-radec.reg', 'r')
    raVals = list();
    decVals = list();
    rArcSecVals = list();
    for line in f:
        justNums = line[7:len(line) - 17]
        nums = justNums.split(",")
        raVals.append(float(nums[0]))
        decVals.append(float(nums[1]))
        rArcSecVals.append(float(nums[2]))
    f.close()

    f2 = open('NGC5194-hardband-good-sources-img.reg', 'r')
    xVals = list();
    yVals = list();
    rVals = list();
    for line in f2:
        justNums = line[7:len(line) - 16]
        nums = justNums.split(",")
        xVals.append(float(nums[0]))
        yVals.append(float(nums[1]))
        rVals.append(float(nums[2]))
    f2.close()

    fileName = raw_input("Enter the name of the fits file: ")
    fileName = 'NGC5194-merged-2to7-asca-im-bin1.fits'

    hdulist = fits.open(fileName)
    hdu = hdulist[0]
    data = hdu.data
    # print data


    offAxes = list();
    cs = list();
    ds = list();
    modelr90s = list();

    cNorm = cls.Normalize(vmin=0, vmax=8)
    scalarMap = cm.ScalarMappable(norm=cNorm, cmap=plt.get_cmap('Set1'))

    for i in range(len(xVals)):  # len(xVals)

        myRs, myCounts, yerr = circleApp(xVals[i] - 1, yVals[i] - 1, rVals[i], data)
        totalC = myCounts[numAps - 1]

        degreeOff = calcOffAxis(raVals[i], decVals[i])

        #r = uniform(0, 1)
        #g = uniform(0, 1)
        #b = uniform(0, 1)

        plt.figure(1)
        plt.errorbar(myRs, myCounts / totalC, yerr=yerr, c=scalarMap.to_rgba(i), fmt='o', label="{0:.2f}".format(round(degreeOff,2)))

        popt, pcov = curve_fit(erfFit, myRs, myCounts / totalC, p0=[2, 1])

        xs, ys = createFitLine(myRs[-1] + 1, erfFit, popt)
        plt.plot(xs, ys, 'r-', c=scalarMap.to_rgba(i))

        plt.figure(i + 4)
        plt.errorbar(myRs, myCounts / totalC, yerr=yerr, c="red", fmt='o')
        plt.plot(xs, ys, 'r-', c="red", label="Original")

        cs.append(popt[0])
        ds.append(popt[1])

        print("Degree off: ", degreeOff)
        print("C: ", popt[0])
        print("D: ", popt[1])

        offAxes.append(degreeOff)

        modelr90s.append(erfFitInv(0.9, *popt))

    plt.figure(1)
    plt.plot((0, 14), (1, 1), 'k-')

    plt.xlabel("Radius (pixels)")
    plt.ylabel("N counts / N tot")
    plt.title("PSFs for Bright Sources")

    ax = plt.subplot(1,1,1)
    handles, labels = ax.get_legend_handles_labels()
    import operator
    print(sorted(labels))
    hl = sorted(zip(handles, labels), key=operator.itemgetter(1))
    handles_sorted, labels_sorted = zip(*hl)
    ax.legend(handles_sorted, labels_sorted, loc="lower right", title="Off Axis (arcmin)")
    #plt.legend(loc="lower right", title="Off Axis (arcmin)")

    plt.figure(2)
    plt.plot(offAxes, cs, 'o', c='blue', label='C')
    plt.plot(offAxes, ds, 'o', c='red', label='D')

    poptC, pcovC = curve_fit(tanhFitCs, offAxes, cs)
    fitCXs, fitCYs = createFitLine(5, tanhFitCs, poptC)
    # fitCs = list()
    # fitRange = np.linspace(0, 4, num=100)
    # for num in fitRange:
    #	fitCs.append(linear(num, *poptC))
    plt.plot(fitCXs, fitCYs, 'r-', c='blue')

    poptD, pcovD = curve_fit(linear, offAxes, ds)
    fitDXs, fitDYs = createFitLine(5, linear, poptD)
    plt.plot(fitDXs, fitDYs, 'r-', c='red')

    print "popt for C: ", poptC
    print "popt for D: ", poptD
    # print("C x intercept: ", tanhFitCsInv(0, *poptC))
    # print("D x intercept: ", invLinear(0, *poptD))

    plt.xlabel("Off Axis (arcmin)")
    plt.ylabel("Constant Value")
    plt.title("Extrapolating Between Functions")
    plt.legend(loc="lower left", title="y = erf(Cx^D)")

    plt.figure(3)
    plt.plot(rVals, [mine - theirs for mine, theirs in zip(modelr90s, rVals)], 'o', c='blue')
    plt.xlabel("Measured r90 (pixels)")
    plt.ylabel("Model r90 - Mesaured r90 (pixels)")
    plt.title("Comparison of r90 Values")

    for i in range(len(xVals)):
        plt.figure(i + 4)
        myC = tanhFitCs(offAxes[i], *poptC)
        myD = linear(offAxes[i], *poptD)
        arg = [myC, myD]
        xs, ys = createFitLine(12, erfFit, arg)
        plt.plot(xs, ys, 'r-', c="blue", label="Modeled")
        plt.xlabel("Radius (pixels)")
        plt.ylabel("N counts/ N tot")
        plt.title("Actual PSF vs Modeled PSF for Off-Axis Angle " + str(round(offAxes[i],2)))
        plt.legend(loc="lower right")

    plt.show()

if __name__ == "__main__":
    main()