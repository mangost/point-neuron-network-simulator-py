#! python
#! -*- coding:UTF8 -*-

# test_lab.py
# A demo to use lab_neu on the center machine

from lab_neu import task_generator, lab
from gen_neu import parameters

# The following part shows how you can effectively and conveniently 
# (re)produce many tasks, 
# for example, you want to test serveral model each with serveral possion rate
# and if the possion rate is less than 0.4, you want to simulate for longer time(1000 ms)
# It could be a lot of boring work if you want to do it manually, but 'task_generator' will do it

pm = parameters()               # Create the default parameters for simulation
pm['t'] = 100                   # You can change the parameters by keys

tg = task_generator(pm)         # Use 'pm' as a ptototype of all tasks' parameters

# You can reproduce many tasks by changing some values of parameters
# tg.add(masks, target, range) will search in tg.pms for those coincide one of the 'masks'
# and replace the vlaue of key 'target' with values in 'range'
tg.add(tg.pms, 'neuron-model', ['HH-PT-GH','HH-GH'])   
tg.add(tg.pms, 'pr', [x/100.0 for x in range(0,100)])

# You can filter the masks for more specific reproduction
masks = [dict(x) for x in tg.pms if x['pr']<0.4 and x['neuron-model']=='HH-PT-GH']   
                                                    # We DEEP copied some pms as masks
                                                    # DEEEEEEP COPY, please
print "tasks generated: %d" % len(masks)                            
for mask in masks:
    mask['neuron-model'] = '*'
            # All values will be matched if you set the value of mask to be '*' 
            # In other words, we ignored the difference of neuron-model
tg.add(masks,'t',[1000])


# Once you have told task_generator what you want to simulate,
# tg,generate will generate all tasks, it's a list of 'Task' instances
tasks = tg.generate()
print([(a.tid, a.pm['neuron-model'],a.pm['pr']) for a in tasks])

# Once you get all the tasks, you can run the 'lab'
HOST = "127.0.0.1"
PORT = 22222        # Servant machine will connect at this HOST and PORT
l = lab(tasks,HOST,PORT,gen_cmd = 'v rm')
        # gen_cmd is the modes of the interface
        # by default, it's v rm
        # v:          verbose process
        # rm:         remove data files after simulation
        # no-rm:      force not to remove data files, you must specific no-rm
        #             if you want to keep the files, since 'rm' is by default on
        # extro-data: reuturn extra-data, including conductance and gating variables.
    
# start assign work, make sure this is started first before all servants
l.start()
