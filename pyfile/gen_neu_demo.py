# gen_neu_demo.py
# A DEMO to gen_neu

from gen_neu import *
from matplotlib import pyplot as plt

pm = parameters()

pm['t'] = 100
pm['dt'] = 1.0/32.0
pm['stv']= pm['dt']
pm['nE'] = 1
pm['pr'] = 0.1
pm['ps'] = 0.014
pm['simulation-method'] = 'simple'
pm['neuron-model'] = 'DIF-GH'
pm['alpha-coefficient'] = 0.01


result = gen_neu(pm,'v nameX')
print "data has been stored in list 'result'"
print [(x[0],x[1]) for x in result]
