#!/usr/bin/python

import os
import sys
import getopt
import aifc
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
	#print strsig
	y = numpy.fromstring(strsig, numpy.short).byteswap()
	y = y.reshape(nframes,nchannels)
	print "aiff", numpy.max(y)
	y = y.astype(float) / 32767
	#x = numpy.asmatrix(y)
	return framerate, y

def fromWavToData(filename):
	fs, y = wavfile.read(filename)
	#print y
	print "wav", numpy.max(y[:,0]), numpy.max(y[:,1])
	y = y.astype(float) / 2147483647
	return fs, y


# from http://stackoverflow.com/questions/10357992/how-to-generate-audio-from-a-numpy-array
def fromDataToWav(data, filename):
	#data = np.random.uniform(-1,1,44100) # 44100 random samples between -1 and 1
	scaled = data#numpy.int16(data/numpy.max(numpy.abs(data)) * 32767)
	wavfile.write(filename, 44100, scaled)

def convolve(data, imp_resp):
	print numpy.max(data), numpy.max(imp_resp[:,0]), numpy.max(imp_resp[:,1])
	l = numpy.convolve(data, imp_resp[:,0])
	r = numpy.convolve(data, imp_resp[:,1])
	result = numpy.vstack((l,r)).T
	print numpy.max(result)
	return result

def main(argv):
	numpy.set_printoptions(threshold=numpy.inf)

	inputfile, outputfile = fromArgsToFileNames(argv)
	fs, data = fromAiffToData(inputfile)


	imp_data = {}

	imp_resp_dir = "HRIRs8Set" 
	imp_resp_files = ["azim0elev0.wav", "azim45elev0.wav", "azim90elev0.wav", "azim135elev0.wav", "azim170elev0.wav", "azim225elev0.wav", "azim270elev0.wav", "azim315elev0.wav"]
	imp_resp_keys = [0, 45, 90, 135, 170, 225, 270, 315]

	#channel_map = [45, 315, 0, -1, 90, 270]
	channel_map = [45, -1, -1, -1, 90, -1]

	for i in range(len(imp_resp_files)):
		fs, single_imp_data = fromWavToData(os.path.join(imp_resp_dir, imp_resp_files[i]))
		imp_data[imp_resp_keys[i]] = single_imp_data
		
	data_out = numpy.zeros((len(data[:,0]) + len(imp_data[0][:,0]) - 1, 2))

	for i in range(6):
		print i, channel_map[i]
		if channel_map[i] >= 0:
			data_out_appendage = convolve(data[:,i], imp_data[channel_map[i]])
			#if i==1:
				#printNonZeros(data_out_appendage)
		elif i==3:
			diff = len(data_out[:,1]) - len(data[:,i])
			data_out_appendage_atom = numpy.lib.pad(data[:,i], (0,diff), 'constant', constant_values=(0,0))
			data_out_appendage = numpy.vstack((data_out_appendage_atom,data_out_appendage_atom)).T

		data_out = numpy.add(data_out, data_out_appendage)


	#print imp_data[90]
	#print imp_data[270]
	#print data_out[0:1000,:]

	#printNonZeros(data_out)

	fromDataToWav(data_out, outputfile)

if __name__ == "__main__":
	main(sys.argv[1:])
