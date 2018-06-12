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

## Programming Practice

This part is just for my hw project.

There are some programming skills that have been applied in this project.

本项目的背景：
计算神经学中常利用各种模型模拟人的神经网络。有时我们会尝试各种模型和参数，希望能解释某一现象或着预测可能会发生的现象。已有几个不错的模拟器，其中包括['point neuron simulation'](https://github.com/mangost/point-neuron-network-simulator)。但该模拟器使用C++编写，不是很便于使用。这个项目包括一个Python借口，用户可以在交互式环境中直接编辑各项参数，无需将其保存成参数文件，即可进行模拟；同时也能直接得到模拟结果。此外，为了方便大量的模拟，这个项目包括一个任务生产器，能抽象地生成大批任务（比如模型为A，B和C，参数为pr = 0,0.01,...,0.99，pr>=0.4只需模拟100ms,但其他的要模拟1000ms，C需要额外参数arg=...，本项目能轻松高效地生成这样的复杂任务，只需简单的几行代码）。最后，此项目利用socket和消息驱动，实现了多终端、多线程模拟（Python的多线程无法真正利用多线程的计算资源，本项目可以通过在一个计算机上的多个端口运行来利用计算机的多线程资源）。

模块化，事件驱动编程： 由于（多个）远程机的进度的不确定性和并行编程的复杂性，本项目采用事件驱动的方法。中心机等待远程机发送连接、申请作业、进度汇报、申请提交等消息，中心机收到消息后决定如何响应。

相关代码：

```
def lab():									# 中心机程序
    def start(self):
        self.s.listen(5)
        while not self.all_finished():
            c, addr = self.s.accept()
            jmsg = json.loads(c.recv(1024))
            title = self.interprete(jmsg)   # 此处解读是哪个远程机，是什么类型的消息
            if title == 'hello':
                sid = None
            else:
                sid = jmsg['sid']
            self.logger('Event',sid,'start()','get connection')

											# 此处对不同消息进行不同的处理，对不同的操作进行模块化

            {
                'hello': self.hello,
                'bye'  : self.bye,
                'error': self.error,
                'report': self.report,
                'pull-request':self.pull_request,
                'task-require':self.task_require,
                'task-process':self.task_process
            }[title](c,jmsg,sid)


            c.close()
        return self.tasks
```

面向对象编程：  
本项目对任务、任务生成器、远程端、中心端进行了合理的抽象，并将其封装成类。

相关代码： 对任务的抽象
```
class task:
    tid= None
    pm = None
    status = 'not-assigned'
    assigned_to = []            # We may assign the same task to various servants in some cases
    time   = [None, None, None] # [expected_time_cost_cmp,expected_time_cost_abs,real_time_cost]
    data   = None               # Finished, data will contain the results from the servant

	(some functions)

# status of an task:
#    not-assigned
#    assigned
#    simulating
#    filtering
#    pulling
#    finished
#    failed
```

Thanks to ['point neuron simulation'](https://github.com/mangost/point-neuron-network-simulator) from which I copied the network files.
