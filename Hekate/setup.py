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

# determine paths
config_file_path = getcwdu() + "\\Hekate\\config.ini"
db_file_path = getcwdu() + "\\web2py\\applications\\Tartaros\\databases\\tartaros.sqlite"
icon_path = "Hekate\\hekate.ico"
bat_path = "Hekate\\hekate.bat"

# import DLLs necessary to run final EXE
from glob import glob
data_files = [
    ("Microsoft.VC90.CRT",
     glob(r'C:\Program Files (x86)\Common Files\microsoft shared\VSTO\10.0\*.dll')),
    ("Hekate", glob(r'%s' % config_file_path)),
    ("web2py\\applications\\Tartaros\\databases", glob(r'%s' % db_file_path)),
    ("", glob(r'%s' % icon_path)),
    ("", glob(r'%s' % bat_path))]

# build application
setup(
    data_files=data_files,
    options={'py2exe': {'bundle_files': 3, 'compressed': True}},
    console=[{
        "script":           "hekate.py",
        "icon_resources":   [(1, icon_path)],
        "dest_base":        "Hekate"
    }],
    zipfile=None
)

# move compiled build folders to artifacts directory
root_dir = getcwdu()
build_src = root_dir + "\\build"
dist_src = root_dir + "\\dist"

# add logs\ directory
try:
    mkdir(dist_src + "\\logs\\")
except WindowsError, e:
    print "Failed to make logs directory."
    print str(e)

# determine destination
dst = root_dir + "\\artifacts"
if not path.exists(dst):
    mkdir(dst)

dst += "\\Hekate"
if path.exists(dst):
    rmtree(dst)

mkdir(dst)

move(build_src, dst)
move(dist_src, dst)