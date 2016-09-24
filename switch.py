#!/usr/bin/python

import os
import sys
import getopt
import aifc
import wave
import numpy
from scipy.io import wavfile

def printNonZeros(data):
	# from http://stackoverflow.com/questions/5488501/filtering-elements-of-matrix-by-row-in-python-scipy-numpy
	a = data
	row = numpy.zeros(len(data[0,:]))
	indices, = (a != row).any(1).nonzero()
	for i in indices:
		print data[i]

# from https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def fromArgsToFileNames(argv):
	inputfile = ''
	outputfile = ''
	try:
		opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
	except getopt.GetoptError:
		print 'test.py -i <inputfile> -o <outputfile>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'test.py -i <inputfile> -o <outputfile>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg
	#print 'Input file is "', inputfile
	#print 'Output file is "', outputfile
	return inputfile, outputfile

# from https://gist.github.com/arunaugustine/5551446
def fromAiffToData(filename):
	s = aifc.open(filename)
	nframes = s.getnframes();
	nchannels = s.getnchannels();
	framerate = s.getframerate();
	strsig = s.readframes(nframes)
	s.close()
	#print strsig
	y = numpy.fromstring(strsig, numpy.short).byteswap()
	y = y.reshape(nframes,nchannels)
	print "aiff", numpy.max(y)
	y = y.astype(float) / 32767
	#x = numpy.asmatrix(y)
	return framerate, y

# from https://gist.github.com/WarrenWeckesser/7461781
def _wav2array(nchannels, sampwidth, data):
    """data must be the string containing the bytes from the wav file."""
    num_samples, remainder = divmod(len(data), sampwidth * nchannels)
    if remainder > 0:
        raise ValueError('The length of data is not a multiple of '
                         'sampwidth * num_channels.')
    if sampwidth > 4:
        raise ValueError("sampwidth must not be greater than 4.")

    if sampwidth == 3:
        a = numpy.empty((num_samples, nchannels, 4), dtype=numpy.uint8)
        raw_bytes = numpy.fromstring(data, dtype=numpy.uint8)
        a[:, :, :sampwidth] = raw_bytes.reshape(-1, nchannels, sampwidth)
        a[:, :, sampwidth:] = (a[:, :, sampwidth - 1:sampwidth] >> 7) * 255
        result = a.view('<i4').reshape(a.shape[:-1])
    else:
        # 8 bit samples are stored as unsigned ints; others as signed ints.
        dt_char = 'u' if sampwidth == 1 else 'i'
        a = numpy.fromstring(data, dtype='<%s%d' % (dt_char, sampwidth))
        result = a.reshape(-1, nchannels)
    return result

def readwav(file):
    """
    Read a wav file.
    Returns the frame rate, sample width (in bytes) and a numpy array
    containing the data.
    This function does not read compressed wav files.
    """
    wav = wave.open(file)
    rate = wav.getframerate()
    nchannels = wav.getnchannels()
    sampwidth = wav.getsampwidth()
    nframes = wav.getnframes()
    data = wav.readframes(nframes)
    wav.close()
    array = _wav2array(nchannels, sampwidth, data)
    return rate, sampwidth, array

def fromWavToData(filename):
	rate, sampwidth, array = readwav(filename)
	#array = array.astype(float) / (2**23 - 1)
#	if filename=='HRIRs8Set/azim90elev0.wav':
#		print array, numpy.max(array)
	return rate, array

#	fs, y = wavfile.read(filename)
#	if filename=='HRIRs8Set/azim90elev0.wav':
#		print y
#	print "wav", numpy.max(y[:,0]), numpy.max(y[:,1])
#	y = y.astype(float) / 2147483647
#	return fs, y


# from http://stackoverflow.com/questions/10357992/how-to-generate-audio-from-a-numpy-array
def fromDataToWav(data, filename):
	#data = np.random.uniform(-1,1,44100) # 44100 random samples between -1 and 1
	scaled = data#numpy.int16(data/numpy.max(numpy.abs(data)) * 32767)
	wavfile.write(filename, 44100, scaled)

def main(argv):
	
	directory = 'KEMAR/diffuse/elev0TWO/'
	for fn in os.listdir(directory):
		filename = os.path.join(directory, fn)
		if os.path.isfile(filename) and fn[0:3] == 'H0e':
			subfn = fn[3:6]
			fnnew = fn[:3] + str(360 - int(subfn)).zfill(3) + fn[6:]
			print 'making', fnnew
			filenamenew = os.path.join(directory, fnnew)
			rate, array = fromWavToData(filename)
			temp = numpy.copy(array[:,0])
			array[:,0] = array[:,1]
			array[:,1] = temp
			fromDataToWav(array, filenamenew)

	
if __name__ == "__main__":
	main(sys.argv[1:])
