#!/usr/bin/env python3
from base import create_output_directory
from timetracker import TimeTracker
from base import get_institutions
from base import ask_continue
from censysfunctions import *
from pathlib import Path
import argparse
import json
import sys
import os

os.chdir(sys.path[0])

parser = argparse.ArgumentParser()
parser.add_argument("input", help="the input file or directory of files to be converted")
parser.add_argument("-y", "--yes", "--assume-yes", help="Automatic yes to prompts; assume \"yes\" as answer to all "
                                                        "prompts and run non-interactively.", action="store_true")
parser.add_argument("-i", "--institutions", help="will add an institution field to every result based on given csv file"
                                                 "in config.ini", action="store_true")
args = parser.parse_args()

print('---Censys converter---')
t = TimeTracker()

institutions = None
if args.institutions:
    institutions = get_institutions()

# A file input
if Path(args.input).is_file():
    convert_file(args.input, 'censys', institutions)

# A directory input
elif os.path.isdir(args.input):
    input_directory = args.input
    files_to_convert = []
    for file in os.listdir(input_directory):
        if file.endswith(".json"):
            files_to_convert.append(file)
    print('These files will be converted: ' + str(files_to_convert))
    print('Total number of files: ' + str(len(files_to_convert)))
    if not args.yes:
        ask_continue()
    output_directory = create_output_directory(input_directory)
    counter = 0
    for input_file in files_to_convert:
        counter += 1
        str_output_file = output_directory + '/' + input_file[:-5] + '-converted.json'
        print('\r' + 'Converting ' + input_file + '[' + str(counter) + '/' + str(len(files_to_convert)) + ']..', end='')
        with open(str_output_file, 'a') as output_file:
            for str_banner in open(input_directory + '/' + input_file, 'r'):
                if str_banner != '\n':
                    banner = dict_clean_empty(json.loads(str_banner))
                    censys_to_es_convert(banner, institutions)
                    output_file.write(json.dumps(banner) + '\n')
    print('\nConverted files written in ' + output_directory)
else:
    msg = "{0} is not an existing file or directory".format(args.input)
    raise argparse.ArgumentTypeError(msg)
t.print_statistics()
