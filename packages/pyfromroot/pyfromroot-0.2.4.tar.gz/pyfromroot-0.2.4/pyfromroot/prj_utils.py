#!/usr/bin/env python3
"""
This is a package to: #***now I try to do globally and better#
 -  systematically load data that are localy here.
 -  replace print function to
     - remove debug  D...
     - print i... stuff to stderr
     - ...
"""

import pkg_resources  # to be able to read data in package
from fire import Fire
import sys
import builtins as __builtin__


# THIS I DONT SEE A POINT..... always returns the same
#par = pkg_resources.Requirement.parse('pandas')
#print("parse://".format(par))
# adds '--' to the package PATH
#print( pkg_resources.resource_filename( 'pandas', '--') )

class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def fail(t):
    print("")
    print(t)
    sys.exit()

def get_file_path(filename):

    """returns full path to data stored in pyfromroot/data"""

    ret = pkg_resources.resource_filename('pyfromroot',
                                        'data/'+filename )
    return ret



def super_print(debug=True):
    """ filename is the file where output will be written"""
    def wrap(func):
        """ func is the function you are "overriding", i.e. wrapping"""
        def wrapped_func(*args,**kwargs):
            """  *args and **kwargs are the arguments supplied
             to the overridden function"""

            #use with statement to open, write to, and close the file safely
            #with open(filename,'a') as outputfile:
            #    outputfile.write(*args,**kwargs)
            #now original function executed with its arguments as normal

            if len(args)>0:
                #print(type(args[0]), args[0])
                if (isinstance(args[0], str)) and (args[0].find("D...")>=0):
                    if not debug:
                        return
            if 'file' in kwargs:
                __builtin__.print(*args, **kwargs )
            else:
                __builtin__.print(*args, **kwargs, file=sys.stderr)
            return #func(*args,**kwargs)
        return wrapped_func
    return wrap

#USE AS print = super_print(debug)(print)
#     print = super_print('output.txt')(print) ... original post

if __name__=="__main__":
    Fire(get_file_path)
