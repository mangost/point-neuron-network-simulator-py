# -*- code: UTF8 -*-

# servant.py
# Running on servant machines
# Note: the def of servant is in lab_neu.py and 
#       this file have nothing to do with it

# TODO logger() at every stage

import socket,time,json,gen_neu

from logger import logger

class Servant:
    s     = None  # socket
                  # NOTICE: it will be opened, connected, closed, reinitialized
                  # for every process

    addr  = None  # address of the center machine
    bs    = 1024
    sid   = None
    status= 'active'

    tasks = []    # [{tid, pm, status, time, data}]
                  # status: assigned, simulating, filtering, finished, failed
                  #                   simulated,  filtered,
    gen_cmd = None
    data_folder = ""
    network_folder = ""

    def start(self):
        self.hello()
        while self.status == 'active':
            if self.next_task() == None:
                self.task_require()      # if no more tasks, status -> 'sleep'
            else:
                task = self.next_task()
                {
                    'assigned':self.simulate,  
                    'simulated':self.filter,  
                    'filtered':self.pull
                }[task['status']](task)


    def __init__(self, center_addr, buffer_size = 1024*8, gen_cmd = None, data_folder = "./data/", network_folder = "./network/"):

        if data_folder[-1] != '/':
            data_folder += '/'
            logger('Warning','ME','__init__()','append "/" to data_folder = %s' % data_folder)
        if network_folder[-1] != '/':
            network_folder += '/'
            logger('Warning','ME','__init__()','append "/" to network_folder = %s' % network_folder)

        self.addr = center_addr
        self.bs   = buffer_size
        self.gen_cmd = gen_cmd
        if gen_cmd != None:
            logger('Event','ME','__init__()','use (specific to servant) gen_cmd = %s'% gen_cmd)

        self.data_folder    = data_folder 
        logger('Event','ME','__init__()','data_folder = %s' % data_folder)
        self.network_folder = network_folder
        logger('Event','ME','__init__()','network_folder = %s' % network_folder)

#    def __del__(self):
#        self.bye()


    def connect(self):
        s = socket.socket()
        try:
            s.connect(self.addr)
        except socket.error as msg:
            logger('Error','ME','connect()',str(msg))
            raise
            
        return s

    def next_task(self, status = '*'):
        for task in self.tasks:
            if task['status'] == status:
                return task
            if status == '*' and task['status'] not in ['failed','finished']:
                return task
        return None

    def add_tasks(self, tasks):
        self.tasks += tasks



    def hello(self):
        s = self.connect()
        s.send(json.dumps({'title':'hello','speed' : None})) # Check if there's bug with NoneType
        rc = s.recv(self.bs)
        assert len(rc) > 0
        jmsg = json.loads(rc)


        if jmsg['title'] == 'task-assign':
            self.sid = jmsg['sid']
            self.add_tasks(jmsg['tasks'])
            if self.gen_cmd == None:
                self.gen_cmd = jmsg['gen_cmd']
                logger('Event','ME','hello()','use (server giving) gen_cmd = %s'%jmsg['gen_cmd'])

        elif jmsg['title'] == 'control':
            self.be_controled(jmsg)
        else:
            logger('Warning','ME','hello()',"jsmg['title'] not understood: %s" % jmsg['title'])
        s.close()

#    def bye(self):
#        if self.status not in ['offline','bye']:
#            try:
#                s = self.connect()
#                s.send(json.dumps({'title':'bye','sid':self.sid})) # Check if there's bug with NoneType
#                s.close()
#            except socket.error as msg:
#                logger('Warning','Center','bye()',str(msg)+"\n Assume that it's offline")
#                self.status = 'offline'
        
    def be_controled(self,jmsg):
        assert jmsg['status'] in ['sleep','bye'] # DEBUG ONLY, currently only 'sleep' is pssible
        if jmsg['status'] == 'sleep' and self.next_task() == None:
            self.status = 'sleep'
        if jmsg['status'] == 'bye':
            self.status = 'bye'


    def task_require(self):
        s = self.connect()
        s.send(json.dumps({'title':'task-require','sid':self.sid})) 
        rc = s.recv(self.bs)
        assert len(rc) > 0
        jmsg = json.loads(rc)
        if jmsg['title'] == 'task-assign':
            self.sid = jsmg['sid']
            self.add_tasks(jmsg['tasks'])
        elif jmsg['title'] == 'control':
            self.be_controled(jmsg)
        else:
            logger('Warning','ME','task_require()',"jsmg['title'] not understood: %s" % jmsg['title'])
        s.close()

    def filter(self,task):
        s = self.connect()
        s.send(json.dumps({'title':'task-process','sid':self.sid,
                           'tid':task['tid'],'status':'filtering'})) 
        s.close()
        task['status'] = 'filtered'
        pass                            # TODO

    def simulate(self, task):
        s = self.connect()
        s.send(json.dumps({'title':'task-process','sid':self.sid,
                           'tid':task['tid'],'status':'simulating'})) 
        s.close()
        
        data = gen_neu.gen_neu(task['pm'],self.gen_cmd,data_folder = self.data_folder, 
                       network_folder = self.network_folder)
        task['data'] = data
        task['status'] = 'simulated'


    def pull(self, task):
        jdata = json.dumps(task['data'])
        # print len(jdata)  # FIXME in linux, there often be bug in reciving data on the server
        s = self.connect()
        s.send(json.dumps({'title':'pull-request','sid':self.sid,
                           'tid':task['tid'], 'data-size':len(jdata)})) 
        rc = s.recv(self.bs)

        if rc != "OK":
            return

        s.send(jdata)
        task['status'] = 'finished'
        
        # Center will assign some tasks
        jmsg = json.loads(s.recv(self.bs))
        if jmsg['title'] == 'task-assign':
            self.sid = jmsg['sid']
            self.add_tasks(jmsg['tasks'])
        elif jmsg['title'] == 'control':
            self.be_controled(jmsg)
        else:
            logger('Warning','ME','pull()',"jsmg['title'] not understood: %s" % jmsg['title'])
        s.close()


#sm = Servant(("127.0.0.1",22268))
#sm.start()
