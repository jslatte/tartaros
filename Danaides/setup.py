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
from os import getcwdu, path, mkdir, makedirs
from shutil import move, rmtree
from time import sleep

####################################################################################################
# Build ############################################################################################
####################################################################################################
####################################################################################################

# determine config file path
output_file_path = getcwdu() + "\\Danaides\\output\\dummy.txt"

# import DLLs necessary to run final EXE
from glob import glob
data_files = [("Microsoft.VC90.CRT",
               glob(r'C:\Program Files (x86)\Common Files\microsoft shared\VSTO\10.0\*.dll'))]

# build application
setup(data_files=data_files, console=['danaides.py'])

# move compiled build folders to artifacts directory
root_dir = getcwdu()
build_src = root_dir + "\\build"
dist_src = root_dir + "\\dist"

# add logs\ directory
mkdir(dist_src + "\\logs\\")

# determine destination
dst = root_dir + "\\artifacts"
if not path.exists(dst):
    mkdir(dst)

dst += "\\Danaides"
if path.exists(dst):
    rmtree(dst)

mkdir(dst)

move(build_src, dst)
move(dist_src, dst)

# add folder for logging output
sleep(3)
makedirs(dst + "\\dist\\Modules\\Danaides\\output\\")