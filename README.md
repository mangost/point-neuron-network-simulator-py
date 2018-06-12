# Python interface to the 'point neuron simulation'

Author: Yongwang SHI <managosteen@sjtu.edu.cn>

This project is the homework project of CS902, lectured by Prof. Chaojun LU

This interface is currently under development, use with care!


## Main features:

- Support the commonly used features of the ['point neuron simulation'](https://github.com/mangost/point-neuron-network-simulator)
- One for all resolution using Python
- Various modes: rm(simulate and remove data files automatially), read(read from data file and proceed filtering and visulizing), nameX(keep data files and return the filenames instead of data)
- lab-neu: automatically generate tasks, distribute to servant machines/processes, simulate and filer in parall, collect data together
- [BUG] With matplotlib to show running plot of the voltage trace interactively
- [Developing] Smart filter: dig out precious data with custom-designed quries


## Overview

There are 3 modules and 3 demos:

Modules:

- gen_neu.py: an interface to ['point neuron simulation'](https://github.com/mangost/point-neuron-network-simulator)
- lab_neu.py: generate tasks and assign to servant machines. Including 
	- time_cost(): compute the expecting time_cost of an task, in unit "per operation"
	- class Task: abstraction of an task, identified by task.tid, parameter for simualtion is stored in task.pm
	- class task_generator: effectively and conveniently generator tasks according to what user's command
	- class lab: waiting for connection from servants, assign tasks and collect data
- servant.py: (class servant_machine) connect to center machine and recive task, simulate, filer(in developing) and return to the center machine

Demos:

- gen_neu_demo.py: how to use gen_neu
- server_demo.py: how to use lab_neu, including generate tasks and start the 'lab'
- servant_demo.py: how to use class servant_machine

## Usage

Please refer to demos and comments at the beginning of each file.
For the interpertation of each neuron models and their parameters, refer to https://github.com/bewantbe/point-neuron-network-simulator

## Bugs:
It is welcomed to tell me any bugs. The following is some bugs that have not repaired so far.

1. Sometimes, center machine recive broken message from the servant, though the buffer is large enough
2. If the center machine is not closed properly, the port can't be released and you need to reassign a PORT if you want to continue.

