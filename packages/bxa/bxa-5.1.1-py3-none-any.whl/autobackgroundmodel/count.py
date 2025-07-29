#!/usr/bin/env python3
"""
Creates background PCA model from a large sample of background spectra
"""
import astropy.io.fits as pyfits
import numpy
import sys

if __name__ == '__main__':
	filenames = sys.argv[1:]
	if len(filenames) == 0:
		sys.stderr.write("""SYNOPSIS: %s <filenames>

Builds a machine-learned background model from a large set of
background spectra (filenames).

Johannes Buchner (C) 2017-2019
""" % sys.argv[0])
		sys.exit(1)
	if len(filenames) == 1:
            filenames = list(map(str.rstrip, open(filenames[0]).readlines()))
	for filename in filenames:
		f = pyfits.open(filename)
		s = f['SPECTRUM']
		print(s.data['COUNTS'].sum(), filename)
		f.close()

