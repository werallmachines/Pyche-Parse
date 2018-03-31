#!/usr/bin/env python3

from __future__ import print_function

'''
Pyche Parse takes error logs and parses them into a more readable format.
Choose a number of lines to display, the values you want to include, and
display them dynamically.

- for now only includes choice of default Apache2 error log values. In
the future this prog will be able to determine which values are enabled
and include more options. 

- only works for error logs. eventually will add functionality for access 
logs as well as error, and output to file.

- only CLI for now. Eventually to include a GUI.
'''

import argparse, collections, os, re, sys

path = '' # path to error log
lines = 0 # lines to display
short_time = False
default = False
values = collections.OrderedDict()
regex = {}
wrapper = [values, regex]

def open_log():
	"Find and open the log file first"
	if os.path.exists(path): # determine if path exists
		try:
			log_file = open(path).readlines()
			if len(log_file) == 0:
				print("FIle is empty.")
				sys.exit(0)
			elif len(log_file) < lines: # if file is shorter than lines
				return log_file
			else:
				slice_bound = len(log_file) - lines # display last n lines
				log_file = log_file[slice_bound:]
				return log_file
		except IOError:
			print(IOError)
			sys.exit(1)
	else:
		print("Path doesn't exist. Please check the path and try again.")

def fill_in_values(log_file):
	"Fill in the dictionary to get ready to print"
	if default:
		for key in values:
			values[key] = init_regex(key, log_file)
	else:
		for key in values:
			if key:
				values[key] = init_regex(key, log_file)

def pyche_print():
	"Display the Apache log file to the user"
	display_string = '====> ' # this will be the format method
	zipped_values = list(zip(*(values[key] for key in values if values[key]))) # pair values together
	for val in range(len(zipped_values[0])): # prepare the format method
		if val != range(len(zipped_values[0]))[-1]: # check if last item in pairing
			display_string += '{' + str(val) + '} | '
		else:
			display_string += '{' + str(val) + '}' # if last item, format appropriately
	for entry in range(len(zipped_values)): 
		popped = zipped_values.pop(0) # pop out each pairing
		print(display_string.format(*popped)) # unpack into format method positionally

def parse_cmdline():
	parser = argparse.ArgumentParser()
	parser.add_argument('path', help='Path to Apache2 file')
	parser.add_argument('-l', '--lines', type=int, help='How many lines to view')
	parser.add_argument('-d', '--default', action='store_true', default=False, help='Include default values')
	parser.add_argument('-t', '--time', action='store_true', help='Convert military time to standard time')
	parser.add_argument('-m', '--module', action='store_true', help='Include module value')
	parser.add_argument('-s', '--severity', action='store_true', help='Include severity value')
	parser.add_argument('-p', '--pid', action='store_true', help='Include PID value')
	parser.add_argument('-c', '--client', action='store_true', help='Include client value')
	parser.add_argument('-e', '--error', action='store_true', help='Include error identification value')
	args = parser.parse_args()

	global path
	global lines
	global values
	global default

	path = args.path
	lines = args.lines if args.lines else 10

	default = args.default
	values['severity'] = args.severity
	values['time'] = args.time
	values['module'] = args.module
	values['pid'] = args.pid
	values['client'] = args.client
	values['error'] = args.error

def init_regex(key, log_file):
	"Perform pattern matching"
	regex['time'] = re.findall(r'\[([\w\s.:]+20\d\d)]', str(log_file))
	regex['module'] = re.findall(r'20\d\d]\s\[([\w]+):\w+\]\s\[pid', str(log_file))
	regex['severity'] = re.findall(r'20\d\d]\s\[[\w]+:([\w]+)]\s\[pid', str(log_file))
	regex['pid'] = re.findall(r'\[(pid\s[\w]+)\]', str(log_file))
	regex['client'] = re.findall(r'\[(client\s[\w.:]*)\]', str(log_file))
	regex['error'] = re.findall(r'\]\s([AH\w\s]*:\s*[\w\s\^\-.,\'":=#<>/\(\)\[\]]*)\\n', str(log_file))

	return regex[key]

if __name__ == '__main__':
	parse_cmdline()
	parse_logfile(open_log())
	pyche_print()



