####################################################################################################
#
# Copyright (c) by Jonathan Slattery for Apollo Video Technology
#
####################################################################################################



####################################################################################################
# Import Modules ###################################################################################
####################################################################################################
####################################################################################################

from Tantalus import Tantalus
from Sisyphus import Sisyphus
from logger import Logger
from sys import argv

####################################################################################################
# Globals ##########################################################################################
####################################################################################################
####################################################################################################

log = Logger()

####################################################################################################
# Run Tantalus #####################################################################################
####################################################################################################
####################################################################################################

# default sys args
output_on = False
num_sites = 255

# read system arguments
params = []
if argv is not None:
    for arg in argv:
        # mode
        if 'output_on=true=' in arg.lower():
            output_on = True
            params.append('Output On:\t%s' % str(output_on))
        elif 'num_sites=' in arg:
            num_sites = int(arg.split('num_sites=')[1])
            params.append('Number of Sites:\t%d' % num_sites)

    # log parameters
    log.trace("Parameters modified:")
    for param in params:
        params[params.index(param)] = param.replace('"', '').replace("'", '')
        log.trace("\t%s" % param)

tantalus = Tantalus(log, Sisyphus, num_sites=num_sites, output_on=output_on)

try:
    tantalus.run_in_dvr_response_simulation_mode()

except BaseException, e:
    log.error("Critical failure occurred.")
    log.error(str(e))
    while True: continue