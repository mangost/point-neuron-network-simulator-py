# gen_neu_demo.py
# A DEMO to gen_neu

from gen_neu import *

pm = parameters()

pm['t'] = 10
pm['nE'] = 10
pm['pr'] = 0.4
pm['ps'] = 0.4
pm['simulation-method'] = 'SSC'

result = gen_neu(pm,'v rm')
print result
