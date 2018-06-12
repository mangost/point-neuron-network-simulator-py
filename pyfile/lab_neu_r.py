#! -*- code:UTF8

# lab_neu.py: 
# time_cost(pm): calculate the expected time cost (relatively, approximation only)
# time_cost_abs(pm, ms_per_operation): (absolutely, approximation only)
# class task: tid, pm, status = 'not-assigned', servant = '', time[0,1,2] = [x,x,None]
# class task_generator(initial): add(mask, target, ranges); generate()
# class lab(tasks, servants): add_task(task), add_servant([(hostname,port)]), start()
#       private: send_msg(servant, msg), send_json(servant, json), send_file(servent, filenames)
#                assign(servant, task),  pull(servant, task)

import gen_neu
import socket

def logger(level, who, where, what):
    print((level, who, where, what))

def time_cost(pm):
    T = pm['t']
    n = pm['nE'] + pm['nI']
    dt= pm['dt']
    pr= pm['pr']
    sp= 1 # TODO: determine it!
    fr= 1 # This is hard to approx before simulation
    factor = 1 - n * fr * dt / 4.0

    return {
            'IF-jump': T * n * (1/dt + pr + n * sp * fr),
            'simple':  T * n * (1/dt + pr),
            'SSC':     T * n * (1/dt + pr + (2 + factor * pr*dt) * n * fr),
            'SSC-Sparse':    T * n * (1/dt + pr + (2 + factor * pr*dt) * n * sp * fr),
            'SSC-Sparse2':   T * n * (1/dt + pr + (2 + factor * pr*dt) * n * sp * fr),
            'big-delay':     T * n * (1/dt + pr + n * sp * fr),
            'big-net-delay': T * n * (1/dt + pr + n * sp * fr),
            'HH-GH-cont-syn':T * (1/dt + pr * n)
            }[pm['simulation-method']]

def time_cost_abs(pm, ms_per_operation):
    return time_cost(pm) * ms_per_operation


# status of an task:
#    not-assigned
#    assigned
#    simulating
#    filtering
#    pulling
#    finished

class task:
    tid= None
    pm = None
    status = 'not-assigned'
    assined_to = []# We may assign the same task to various servants in some cases
    time   = [None, None, None]
    data   = None  # Finished, data will contain the results from the servant

    def __init__(self, tid, pm):
        self.tid= tid
        self.pm = pm
        self.time[0] = time_cost(pm)
        self.time[1] = self.time[0]

    def to_tuple(self):
        return (tid, pm, status, assigned_to, time, data)


# class task_generator(initial): add(masks,target, ranges); generate()
class task_generator:
    tasks = []
    pms   = []

    def __init__(self, pm_prototype = None):
        if pm_prototype == None:
            self.pms.append(gen_neu.parameters())
        else:
            self.pms.append(pm_prototype)

    def add(self, masks, target, ranges):
        pms = []
        for mask in masks:
            for pm in self.pms:
                print("pm")
                if self.coincide(pm, mask):
                    if target == "delete":
                        pass # Avoid else part
                    else:
                        for one in ranges:
                            n = dict(pm) # Force to get a copy instead of reference
                                         # IMPROVE: if there a better way to do this?
                            n[target] = one
                            pms.append(n)
                else:
                    pms.append(pm)
                
        self.pms = pms

    def add_some(self, pms):
        self.pms += pms

    def delete(self, masks):
        self.add(self, masks,"delete",[])

    def generate(self):
        self.tasks = []
        for i in range(len(self.pms)):
            self.tasks.append(task(i, self.pms[i]))
        return self.tasks

    # It shall be static, not knowing how to do it in Python TODO
    def coincide(self, pm, mask):
        for each in mask:
            if mask[each] != "*" and (not each in pm or pm[each] != mask[each]):
                return False
        return True
        
# class lab(tasks, servants): add_task(tasks), add_servant([(hostname,port)]), start()
#       private: (not employed yet)send_file(servent, filenames)
#                assign_auto & assign(servant, task),  pull(servant, task)
class lab:
    tasks = []
    servants = {} # we will listen
                  # {((hostname, port): {speed, task_assigned(list of tid), status, last_response}}
    s = socket.socket()

    def __init__(self, tasks,hostname,port,servants = []):
        self.tasks = tasks
        self.servant = servants
        self.s.bind((hostname,port))

    def add_tasks(sefl, tasks):
        self.tasks += tasks


    def add_servant(self, addr, task_assigned = [], speed, status):
        self.servants[addr] = {'speed':speed, 
                'task_assigned':[], 
                'status':status,
                'last_response': time.time()
                }
   

    def start(self):
        s.listen(5)
        while True:
            c, addr = s.accept()
            jmsg = json.load(c.recv(1024))
            {
                'hello': self.hello(c,jmsg,addr),
                'bye'  : self.bye(c,jmsg,addr),
                'error': self.error(c,jmsg,addr),
                'report': self.report(c,jmsg,addr),
                'pull_request':self.pull_request(c,jmsg,addr),
                'task_require':self.task_require(c,jmsg,addr),
                'task_process':self.task_process(c,jmsg,addr):
            }[self.interprete(jmsg)]
            


    # This function below shall be static! IMPROVE
    def interprete(self,jmsg):
        return msg['title']

    
    def hello(self,c,jmsg,addr):
        # hello|[json data: speed(int)]
        speed = json.load(jmsg['speed'])
        self.add_servant(addr, [], speed, 'active')
        assign_auto(addr)

    def bye(self,c,jmsg,addr):
        self.servants[addr][status] = 'bye'

    def error(self,c,jmsg,addr):
        logger("Error", addr, "lab.error()", jmsg)

    def report(self,c,jmsg,addr):
        self.servants[addr][status] = jmsg['status']

    def task_process(self,c,jmsg,addr):
        tasks = [x for x in self.tasks if x.tid != jmsg['tid']]
        found = [x for x in self.tasks if x.tid == jmsg['tid']]
        assert len(found)==1
        found[0].status = jmsg['status']
        self.tasks = found + tasks
        logger("Event", addr, "lab.process()","task (tid = %d) change status to %s" % jmsg['tid'],jmsg['status'])


    def pull_request(self,c,jmsg,addr),
        data_size = jmsg['data_size']
        tid       = jmsg['tid']
        # Equvi to: self.servant[addr][status] = 'pulling'
        jmsg['status'] = 'pulling'
        self.report(c,jmsg,addr)
        self.task_process(c,jmsg,addr)

        c.send("OK")
        data = json.load(c.recv((int(data_size/1024)+1)*1024))
        for each in self.tasks:
            if each.tid == tid:
                each.data = data
                each.status = 'finished'
        
        # Send addr to the servent
        # Let another process to recieve the data
        # TODO

        assign_auto(addr)



    def self.task_require(self,c,jmsg,addr)
        assign_auto(addr)

        

