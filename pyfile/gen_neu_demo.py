# gen_neu_demo.py
# A DEMO to gen_neu

from gen_neu import *
from matplotlib import pyplot as plt

pm = parameters()

pm['t'] = 100
pm['nE'] = 10
pm['pr'] = 1
pm['ps'] = 0.14
pm['simulation-method'] = 'simple'
pm['neuron-model'] = 'DIF-GH'
pm['alpha-coefficient'] = 0.01


result = gen_neu(pm,'v rm')
print "data has been stored in list 'result'"
print [(x[0],x[1]) for x in result]
