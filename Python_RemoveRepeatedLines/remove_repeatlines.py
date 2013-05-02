#!/usr/bin/python2.4
#
# Copyright 2010-2012 Google Inc. All Rights Reserved.

"""Renderscript Compiler Test.

Runs subdirectories of tests for the Renderscript compiler.
"""

#import filecmp
#import glob
import os
#import re
#import shutil
#import subprocess
import sys

__author__ = 'Android'

class Options(object):
    def __init__(self):
    return
  verbose = 0
  maxrepeat = 4
  
def Usage():
  """Print out usage information."""
  print ('Usage: %s in.txt\n'
         'Remove repeated lines. Keywords is IN or OUT.\n'
         'Available Options:\n'
         '  -h, --help          Help message\n'
         '  -max n              Max. repeat num\n'
         '  -v, --verbose       Verbose output\n'
        ) % (sys.argv[0]),
  return

def HandleFiles(src, dst):
  """Update dst if it is different from src."""
  oldmode = -1 #@IndentOk
  count = 0
  print 'Copying from %s to %s' % (src, dst)
  f = open(src, "r")
  w = open(dst, "w")
  while(True):
	line = f.readline()
	if len(line) == 0: break;
	
	mode = 0 #@IndentOk
	if (line.find('OUT') != -1):
		mode = 1
	elif (line.find('IN') != -1):
		mode = 2
	
	if (mode == 0):
		w.writelines(line)
		oldmode = 0
		count = 0
	else:
		if (mode != oldmode):
			oldmode = mode
			count = 0
		else:
			count += 1
		
		if (count < 4):
			w.writelines(line)
		else:
			w.writelines('repeat.......................\n')
		
	#print 'mode is %d' % mode
	#w.writelines(line + "tommy")
  
  f.close()	
  w.close()	
  
  return 0
  
##################################################################
def main():
  passed = 0
  failed = 0
  files = []
  failed_tests = []
  fout = 'out.txt'

  if len(sys.argv) < 2:
	Usage()
	return 0
  
  for arg in sys.argv[1:]:
    if arg in ('-h', '--help'):
      Usage()
      return 0
    elif arg in ('-v', '--verbose'):
      Options.verbose += 1
    else:
      # Test list to run
      if os.path.isfile(arg):
		fin = arg
		print 'try to handle file %s\n' % fin
		HandleFiles(fin, fout)
		return 0
      else:
        print >> sys.stderr, 'Invalid file: %s' % arg
        return 1

  return failed != 0


if __name__ == '__main__':
  sys.exit(main())
