#! -*- code:UTF8

# lab_neu.py: 


# time_cost(pm): calculate the expected time cost (relatively, approximation only)
# time_cost_abs(pm, ms_per_operation): (absolutely, approximation only)


#class task:
#    tid= None
#    pm = None
#    status = 'not-assigned'
#    assigned_to = []            # We may assign the same task to various servants in some cases
#    time   = [None, None, None] # [expected_time_cost_cmp,expected_time_cost_abs,real_time_cost]
#    data   = None               # Finished, data will contain the results from the servant
#
# status of an task:
#    not-assigned
#    assigned
#    simulating
#    filtering
#    pulling
#    finished
#    failed


# class task_generator
#    self.pms
#    self.tasks
#
#    def __init__(self, pm_prototype = None):   If being None, it will use gen_neu.parameters() 
#
#    def add(self, masks, target, ranges):      pm in self.pms that 'coincide' one of the masks
#                                               will be updated: it will be removed while
#                                               reproduce some with 'target' being one of'ranges'
#
#    def add_some(self, pms):                   Just add pms to self.pms
#    def delete(self, masks):
#    def generate(self):                        Generate tasks and return them
#    def coincide(self, pm, mask):              Static! To check if pm statisfy the mask, that is
#                                               pm has all the (key,value) same as maske,
#                                               except for those with value "*"

#class servant:
#    sid = None
#    status= 'unknown'                          pissible status:
#                                               unknown, active, sleep, offline, bye
#    speed = None
#    task_assigned = []  # list of tid
#    last_response = None

# class lab:
# public:
#    tasks = []
#    servants = []
#    def add_tasks(self, tasks):
#    def add_servant(self, speed = None, status = 'unknown', task_assigned = []):
#    def start(self):
# private:
#    def find_servant(self,sid):
#    def interprete(self,jmsg):
#    def hello(self,c,jmsg,sid = None):
#    def bye(self,c,jmsg,sid):
#    def error(self,c,jmsg,sid):
#    def report(self,c,jmsg,sid):
#    def task_process(self,c,jmsg,sid):
#    def pull_request(self,c,jmsg,sid):
#    def task_require(self,c,jmsg,sid):
#    def assign_auto(self,c, sid):     
#    def assign(self, c, sid, task):
#    def ctrl_servant(self, c, sid, status):

import gen_neu
import socket
import json
import time

import logger as log
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
#    failed

class task:
    tid= None
    pm = None
    status = 'not-assigned'
    assigned_to = []            # We may assign the same task to various servants in some cases
    time   = [None, None, None] # [expected_time_cost_cmp,expected_time_cost_abs,real_time_cost]
    data   = None               # Finished, data will contain the results from the servant

    def __init__(self, tid, pm):
        self.tid= tid
        self.pm = pm
        self.time[0] = time_cost(pm)
        self.time[1] = self.time[0]

    def to_dict(self):
        return {'tid':self.tid,
                'pm':self.pm, 
                'status':self.status, 
                'assigned_to':self.assigned_to, 
                'time':self.time, 
                'data':self.data
                }


# class task_generator
#    def __init__(self, pm_prototype = None):   If being None, it will use gen_neu.parameters() 
#
#    def add(self, masks, target, ranges):      pm in self.pms that 'coincide' one of the masks
#                                               will be updated: it will be removed while
#                                               reproduce some with 'target' being one of'ranges'
#
#    def add_some(self, pms):                   Just add pms to self.pms
#    def delete(self, masks):
#    def generate(self):
#    def coincide(self, pm, mask):              Static! To check if pm statisfy the mask, that is
#                                               pm has all the (key,value) same as maske,
#                                               except for those with value "*"

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
                    pass
                    #pms.append(pm)      # FIXED
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

class servant:
    sid = None
    status= 'unknown'   #pissible status: unknown, active, sleep, offline, bye
    speed = None        
    task_assigned = []  # list of tid
    last_response = None

    def __init__(self, sid, status = 'unknown', speed = None, task_assigned = [], last_response = None):
        self.sid = sid
        self.status = status
        self.speed  = speed
        self.task_assigned = task_assigned
        self.last_response = last_response
        
# class lab:
# public:
#    tasks = []
#    servants = []
#    def add_tasks(self, tasks):
#    def add_servant(self, speed = None, status = 'unknown', task_assigned = []):
#    def start(self):
# private:
#    def find_servant(self,sid):
#    def interprete(self,jmsg):
#    def hello(self,c,jmsg,sid = None):
#    def bye(self,c,jmsg,sid):
#    def error(self,c,jmsg,sid):
#    def report(self,c,jmsg,sid):
#    def task_process(self,c,jmsg,sid):
#    def pull_request(self,c,jmsg,sid):
#    def task_require(self,c,jmsg,sid):
#    def assign_auto(self,c, sid):     
#    def assign(self, c, sid, task):
#    def ctrl_servant(self, c, sid, status):

class lab:
    tasks = []
    servants = []
    waiting_num = 2
    gen_cmd  = ""


    s = socket.socket()
    logger = None
    
    def __del__(self):
        self.s.close()

    def __init__(self,tasks,hostname,port,waiting_num = 2,servants = [],gen_cmd = 'rm v',log= log.logger):
        self.tasks = tasks
        self.waiting_num = waiting_num
        self.servants = servants
        self.s.bind((hostname,port))
        self.gen_cmd = gen_cmd
        self.logger = log

    def add_tasks(self, tasks):
        self.tasks += tasks


    def add_servant(self, speed = None, status = 'unknown', task_assigned = []):
        sid =len(self.servants)
        self.servants.append(servant(sid, status,speed, task_assigned, time.time()))
        self.logger('Event',sid,'add_servant()','')
        return sid
   
    def find_servant(self,sid):
        for each in self.servants:
            if each.sid == sid:
                return each
        return None

    def all_finished(self):
        for task in self.tasks:
            if task.status not in ['finished','failed']:
                return False
        return True


    def start(self):
        self.s.listen(5)
        while not self.all_finished():
            c, addr = self.s.accept()
            jmsg = json.loads(c.recv(1024))
            title = self.interprete(jmsg)
            if title == 'hello':
                sid = None
            else:
                sid = jmsg['sid']
            self.logger('Event',sid,'start()','get connection')
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
            


    def interprete(self,jmsg):
        if 'sid' in jmsg:
            ref =  self.find_servant(jmsg['sid'])
            if ref != None:
                ref.last_response = time.time()
        return str(jmsg['title'])

    
    def hello(self,c,jmsg,sid = None):
        assert sid == None
        speed = jmsg['speed']
        sid = self.add_servant(speed, 'active',[])
        self.assign_auto(c,sid, self.waiting_num)  # In assign() we will tell the servant its id

    def bye(self,c,jmsg,sid):
        self.find_servant(jmsg['sid']).status = 'bye'

    def error(self,c,jmsg,sid):
        raise ValueError # DUBUG
        self.logger("Error", sid, "lab.error()", jmsg)

    def report(self,c,jmsg,sid):
        self.find_servant(sid).status = jmsg['status']

    def task_process(self,c,jmsg,sid):
        tasks = [x for x in self.tasks if x.tid != jmsg['tid']]
        found = [x for x in self.tasks if x.tid == jmsg['tid']]
        assert len(found)==1
        found[0].status = jmsg['status']
        if 'time' in jmsg: 
            found[0].time = jmsg['time']
        self.tasks = found + tasks
        self.logger("Event", sid, "process()","task (tid = %d) change status to %s" %
                (jmsg['tid'],jmsg['status']))


    def pull_request(self,c,jmsg,sid):
        data_size = jmsg['data-size']
        tid       = jmsg['tid']
        jmsg['status'] = 'pulling'
        self.report(c,jmsg,sid)
        self.task_process(c,jmsg,sid)

        c.send("OK")  # Note: no json.loads

        # FIXME  sometimes json.loads can't decode rc, possibly cuz too small buffer size
        self.logger("DEBUG",sid,"pull_request","data_size = %d"%data_size)
        self.logger("DEBUG",sid,"pull_request","buffer_size= %d"%((int(data_size/1024)+1)*1024))
        
        rc = c.recv(data_size)
        self.logger("DEBUG",sid,"pull_request","len(reviced_msg)= %d"%len(rc))
        self.logger("DEBUG",sid,"pull_request","reviced_msg[-50:]= %s"%rc[-50:])

        assert len(rc) > 1
        data = []  # FIXED 2018/06/15
        try:
            data = json.loads(rc)
        except ValueError as msg:
            self.logger('Error',sid,'pull_request()','json.load() failed, with error'+str(msg))
        for each in self.tasks:
            if each.tid == tid:
                each.data = data
                each.status = 'finished'
        
        # Let another process to recieve the data
        # TODO
    
        sid = jmsg['sid']
        self.assign_auto(c,sid)



    def task_require(self,c,jmsg,sid):
        self.assign_auto(c,sid)

    def assign_auto(self,c, sid, num = 1):     
        assert [x for x in self.servants if x.sid == sid] != []
        to_assign = []

        for each in self.tasks:
            if each.status == 'not-assigned':
                to_assign.append(each)

        if to_assign == []:
            self.ctrl_servant(c,sid,'sleep')
        else:
            num = min([num, len(to_assign)])
            print "#task to be assigned %d" % num
            self.assign(c,sid,to_assign[0:num])
            self.logger('Event',sid,'assign_auto()','tasks to be assigned: %s' % str([x.tid for x in to_assign[0:num]]))
            return


        # IMPROVE deliver task based on the expected time cost and servant's speed


    def assign(self, c, sid, tasks):
        for task in tasks:
            task.status = 'assigned'
            task.assigned_to.append(sid)

        c.send(json.dumps({'title':'task-assign',
                           'tasks':[task.to_dict() for task in tasks],
                           'gen_cmd':self.gen_cmd,
                           'sid':sid}))


    # possible status of a servant
    # unknown, active, sleep, offline, bye
    def ctrl_servant(self, c, sid, status):
        c.send(json.dumps({'title':'control','status':status}))
        self.find_servant(sid).status = status

    # TODO task_recall
