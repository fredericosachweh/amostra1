#!/usr/bin/python
import sys
import getopt
from lxml import etree
import glob


def main(argv):
    input_folder = ''
    try:
        opts, args = getopt.getopt(argv, "hi:")
    except getopt.GetoptError:
        print 'validation.py -i <input folder>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'validation.py -i <input folder>'
            sys.exit()
        elif opt in ("-i"):
            input_folder = arg
    if input_folder == '':
        print 'validation.py -i <input folder>'
        sys.exit(2)

    xmlfiles = glob.glob(input_folder + "*.xml")

    for f in xmlfiles:
        print f
        tree = etree.parse(f)
    print 'Validation - Success'

if __name__ == "__main__":
    main(sys.argv[1:])
