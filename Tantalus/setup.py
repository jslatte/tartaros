####################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################

####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from distutils.core import setup
import py2exe
from os import getcwdu, path, mkdir
from shutil import move, rmtree

####################################################################################################
# Build ############################################################################################
####################################################################################################
####################################################################################################

# determine config file path
output_file_path = getcwdu() + "\\Modules\\Tantalus\\output\\output.txt"
config_file_path = getcwdu() + "\\Modules\\Tantalus\\config.ini"

# import DLLs necessary to run final EXE
from glob import glob
data_files = [("Microsoft.VC90.CRT",
               glob(r'C:\Program Files (x86)\Common Files\microsoft shared\VSTO\10.0\*.dll')),
               ("Modules\\Tantalus\\output", glob(r'%s' % output_file_path)),
               ("Modules\\Tantalus\\", glob(r'%s' % config_file_path))]

# build application
setup(data_files=data_files,
    console=['tantalus.py'])

# move compiled build folders to artifacts directory
root_dir = getcwdu()
build_src = root_dir + "\\build"
dist_src = root_dir + "\\dist"

# determine destination
dst = root_dir + "\\artifacts"
if not path.exists(dst):
    mkdir(dst)

dst += "\\Tantalus"
if path.exists(dst):
    rmtree(dst)

mkdir(dst)

move(build_src, dst)
move(dist_src, dst)