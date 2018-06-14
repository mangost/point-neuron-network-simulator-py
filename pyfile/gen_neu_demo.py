# gen_neu_demo.py
# A DEMO to gen_neu

from gen_neu import *
from matplotlib import pyplot as plt

# Get defalut parameters
pm = parameters()

# Customize parameters
    # basic ones
pm['simulation-method'] = 'simple' # it could be simple, SSC(spike order corrction) 
                                   # and (NOt TESTED YET:) IF-jump, etc(refer to 
                                   # https://github.com/bewantbe/point-neuron-network-simulator)
pm['neuron-model'] = 'HH-PT-GH' # it could be HH-PT-GH, LIF-G, LIF-GH, DIF-GH, DIF-single-GH, etc
                                # refer to the link above
pm['net']           # the adjacent matrix of the neruon net(system)
                    # you can fill in a path or a list of list (matrix)
                    # by default it's -, which means all neuron connected

pm['t'] = 100       # the lasting time of simulation
pm['dt'] = 1.0/32.0 # the duration of a small time step
pm['stv']= pm['dt'] # the duration of one data record
pm['nE'] = 1        # number of excititory neurons (neurons that gives a positive inplus)
pm['nI'] = 0        # number of inhibitory neurons (neurons that gives a negative inplus)

    # more advanced para
pm['pr'] = 0.1      # poisson rate (the probability of a random input, 
                    # to simulate the complicated network connection of human neuron system
pm['ps'] = 0.014    # poisson strength, not to be too large
pm['scee'] = 0.05   # the effect of one fired 'e'xcititory neuron giving to a connected 'e' one
pm['scei'] = 0.05   # the effect of one fired 'e'xcititory neuron giving to a connected 'i' one
pm['scie'] = 0.05   # the effect of one fired 'i'xcititory neuron giving to a connected 'e' one
pm['scii'] = 0.05   # the effect of one fired 'i'xcititory neuron giving to a connected 'i' one


# call the simulator and run simulation.
result = gen_neu(pm,'v rm')  # the second parameter could be 
# v: default, verbose, print process
# rm:default, remove data files (you can the content via return value)
# no-rm: force not to remove data files
#        NOTICE: rm is by default on, even if you do not specify it
#                if you want to keep the files, you MUST specify no-rm
# read:  do not do simulation but read existing files
#        useful when you 'no-rm' and clear the return value
# nameX: do not return data, only return filenames
#        in this mode, no-rm is forced on
# cmd:   do not do simultation but print the command line options
#        that "is" going to be executed, useful for test and debug


# after simulation 
print "data has been stored in list 'result'"
print [(x[0],x[1]) for x in result] #x[2] is data itself, you can use it


plt.plot(result[0][2][0])  # the voltage trace of the first neruron
plt.show()
