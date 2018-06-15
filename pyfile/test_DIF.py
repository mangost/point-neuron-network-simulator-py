# gen_neu_demo.py
# A DEMO to gen_neu


# This demo shows how to use gen_neu
# and more usefully, how to use gen_neu to validate and find new phenomenon

# In this demo, we use DIF, an adapted version of LIF, proposed by Douglous et al.
# the part of simuation program is implemented by mangost, as well as this demo

# we will simulate how a neuorn behave when it revieve 2 events, one excitatory and one inhibitory
# you will find it is not simply the sum of the effect of each event


from gen_neu import *
from matplotlib import pyplot as plt

pm = parameters()

pm['t'] = 100
pm['dt'] = 1.0/32.0
pm['stv']= pm['dt']
pm['nE'] = 1
pm['pr'] = 0.0              # no poisson to make the phenmenon clear
pm['ps'] = 0.0
pm['simulation-method'] = 'simple'
pm['neuron-model'] = 'DIF-GH'
pm['alpha-coefficient'] = 0.01
pm['input-event-path'] = 'params\input3_12.txt' # input two events simutaneously
                                                # one exictatory with strength 0.1
                                                # the other inhibitory with strength 0.12


result_both = gen_neu(pm,'v rm')
#print "data has been stored in list 'result'"
# print [(x[0],x[1]) for x in result]
voltage_both = result_both[0][2][0]

pm['input-event-path'] = 'params\input3_1.txt' # only exictatory event
result_ex_only = gen_neu(pm,'v rm')
voltage_ex = result_ex_only[0][2][0]


pm['input-event-path'] = 'params\input3_2.txt' # only inhibitory event
result_in_only= gen_neu(pm,'v rm')
voltage_in = result_in_only[0][2][0]


xline = [x/32.0 for x in range(len(voltage_both))]
plt.plot(xline, voltage_ex)
plt.plot(xline, voltage_in)
plt.legend(["excitatory only", "inhibitory only"])
plt.xlabel("t/ms")
plt.ylabel("V/1")
plt.show(block = False)

plt.figure()
voltage_linear = [voltage_ex[i] + voltage_in[i] for i in range(len(voltage_ex))]
plt.plot(xline, voltage_both)
plt.plot(xline, voltage_linear)
plt.legend(["simulation of both ex and in", "the sum of ex and in"])
plt.xlabel("t/ms")
plt.ylabel("V/1")
plt.show()
