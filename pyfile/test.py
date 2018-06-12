#! python
#! -*- coding:UTF8 -*-

# test_lab.py
# A demo to use lab_neu on the center machine

from lab_neu import task_generator, lab
from gen_neu import parameters

pm = parameters()               # Create the default parameters for simulation
pm['t'] = 10000                 # You can change the parameters by keys
tg = task_generator(pm)         # Use 'pm' as a ptototype of all tasks' parameters
tg.add(tg.pms, 'pr', [1,2,3])   # You can reproduce many tasks by changing some values of parameters

tasks = tg.generate()
print([(a.tid, a.status) for a in tasks])

l = lab(tasks,"127.0.0.1",12346,gen_cmd = 'v no-rm')
l.start()
