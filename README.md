# Python interface to the 'point neuron simulation'

Author: Yongwang SHI <managosteen@sjtu.edu.cn>

This interface is currently under development, use with care!


Main features:

- Support the commonly used features of the 'point neuron simulation'
- One for all resolution using Python
- [Experimental] With matplotlib to show running plot of the voltage trace interactively
- Various modes: rm(simulate and remove data files automatially), read(read from data file and proceed filtering and visulizing), nameX(keep data files and return the filenames instead of data)
- [Developing] lab-neu: automatically generate tasks, distribute to servant machines/processes, simulate and filer in parall, collect data together
- [Developing] Smart filter: dig out precious data with custom-designed quries



task:
tid
pm
status
servant
time[0,1,2]:
time_cost_expect
time_cost_remain_expect
time_cost_actual


status of an task:

not-assigned
assigned
simulating
filtering
pulling
finished

