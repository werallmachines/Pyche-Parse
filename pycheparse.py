#!/usr/bin/env python

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

import collections
import argparse
import sys
import os
import re

path = '' #log location
lines = 10 #lines to display
short_time = False
values = collections.OrderedDict()
values['time'] = ''; values['module'] = ''; values['pid'] = ''; values['client'] = ''; values['error'] = ''

class Pycheparse:
    def __init__(self):
        pass

    def open_log(self):
        '''
        Find and open the log file first
        '''
        if os.path.exists(path): #first determine if the user given path exists
            try:
                logf = open(path).readlines()
                if len(logf) == 0: #pyche parse won't wont work an empty file
                    print("File is empty. Please choose file with content.")
                    sys.exit(1)
                elif len(logf) < lines: #if log file is shorter than requested lines, display whole log file
                    return logf
                else:
                    slice_bound = len(logf) - lines #display the last n number of lines
                    log = logf[slice_bound:]
                    return log
            except OSError: #in case of permissions issue
                print(OSError)
                sys.exit(1)
        else:
            print("Given path does not exist. Check path and try again.")

    def parse_log(self, log):
        '''
        Parse the log file after the necessary lines extracted
        '''
        if values['time']:
            values['time'] = re.findall(r'\[([\w\s.:]+20\d\d)]', str(log))
        if values['module']:
            values['module'] = re.findall(r'20\d\d]\s\[([\w:]+)\]\s\[pid', str(log))
        if values['pid']:
            values['pid'] = re.findall(r'\[(pid\s[\w]+)\]', str(log))
        if values['client']:
            values['client'] = re.findall(r'\[(client\s[\w.:]*)\]', str(log))
        if values['error']:
            values['error'] = re.findall(r'\]\s([AH\w\s]*:\s*[\w\s\^\-.,\'":=#<>/\(\)\[\]]*)\\n', str(log))

    def pyche_print(self):
        '''
        Display the Apache log to the user
        '''
        #first prepare the display string
        display_string = "==> " #string we'll be printing
        zipped_values = zip(*(values[key] for key in values if values[key])) #take the dictionary values and pair them
        for val in range(len(zipped_values[0])): #format display string
            if val != range(len(zipped_values[0]))[-1]:
                display_string += "{" + str(val) + "} | "
            else:
                display_string += "{" + str(val) + "}"
        #remove entries from the zipped list, add to format method and print
        for entry in range(len(zipped_values)):
            popped = zipped_values.pop(0)
            print(display_string.format(*popped))

def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="Path to Apache2 log file")
    parser.add_argument('-l', '--lines', type=int, help="How many lines to view")
    parser.add_argument('-s', '--shorttime', action="store_true", help="Display time without day or seconds")
    parser.add_argument('-t', '--time', action="store_true", help="Convert militarytime to standard time")
    parser.add_argument('-m', '--module', action="store_true", help="Include module value")
    parser.add_argument('-p', '--pid', action="store_true", help="Include PID value")
    parser.add_argument('-c', '--client', action="store_true", help="Include client value")
    parser.add_argument('-e', '--error', action="store_true", help="Include error identification value")
    args = parser.parse_args()

    global path
    global lines
    global short_time

    path = args.path
    lines = args.lines
    short_time = args.shorttime

    values['time'] = args.time
    values['module'] = args.module
    values['pid'] = args.pid
    values['client'] = args.client
    values['error'] = args.error

if __name__ == "__main__":
    pycheparse = Pycheparse()
    parse_cmdline()
    pycheparse.parse_log(pycheparse.open_log())
    pycheparse.pyche_print()
