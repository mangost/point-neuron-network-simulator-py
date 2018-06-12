#! -*-coding=UTF-8-*-

# Neuron network simulator (interface to gen_neu).

import time
import os
import subprocess, sys
import array     # to read binary file - vlotage data

def parameters():
    pm = {
            'prog_path'   :['../bin/gen_neu'],
            'neuron-model':'HH-PT-GH',
            'simulation-method' :'SSC',
            'net'         :'-',
            'nE'          :1,
            'nI'          :0,
            #'net_path'    :None,
            #'net_adj'     :[]
            'pr'  :0,
            'ps'  :0,                
            'pri' :0,              
            'psi' :0,
            'scee':0,
            'scie':0,
            'scei':0,
            'scii':0,
            #'extI':0,
            #'sine_amp'
            #'sine_freq'
            't'   :1e4,
            'dt'  :1.0/32,
            'stv' :0.5,
            't-warming-up'      :0,
            'seed'              :'auto',
            # Not in matlab interface:
            'volt-path':'',
            'isi-path':'',
            'ras-path':'',



            # End Not in matlab interface
            #'spike_threshold'   :[],
            #'synaptic_delay'
            #'synaptic_net_delay'
            #'tau_g_path'
            #'tau_g'
            #'initial_state_path'
            #'initial_state'
            #'neuron_const_path'
            #'neuron_const'
            #'input_event'
            #'force_spikes'
            #'prog_path'
            #'output_poisson_path'
            #'parameter_path'
            'extra_cmd':'',
            # Recognized parameter
            #'scee_mV':0,
            #'scie_mV':0,
            #'scei_mV':0,
            #'scii_mV':0,
            #'ps_mV'  :0,
            #'psi_mV' :0
        }
    return pm



def dbp(string, verbose = 1):
    if verbose:
        print string

# MAIN FUNCTION
def gen_neu(pm, gen_cmd = 'rm v', data_folder = "./data/", network_folder = "./network/"):

    # in case someone forget '/'
    if data_folder[-1] != '/':
        data_folder += '/'
    if network_folder[-1] != '/':
        network_folder += '/'

    pm2 = pm
    gen_cmds = gen_cmd.replace(',',' ').split()

    # need help?
    if 'h' in gen_cmds or 'help' in gen_cmds:
        print help_msg

    # detect modes
    modes = get_modes(gen_cmds)

    check_parameters(pm2)

    exec_path = find_exec_path(pm2)

    cmd_str = get_cmd_str(pm2,modes) # if in mode 'read', return ""

    cmd_str,filenames = add_exec_and_data_path(pm2,cmd_str,exec_path,data_folder,modes)

    if modes['cmd']:
        print "The cmd_str that is going to (in fact won't) be called is: "
        print cmd_str
        return 0

    if modes['read']:
        # We have get and checked the filenames in 'add_exec_and_data_path'
        # Nothing to do but just to avoid simulation
        pass
    else:
        # start simulating!
        (output, err, p_status) = run_cmd(cmd_str, modes)
    
        if p_status != None and p_status != 0:
            dbp("err occure in simulation")
            return -1 # BETTER warnning?


    # by now, data shall be generated

    # mode nameX means the user require filenames only
    if modes['nameX']:
        return filenames

    data = read_data_from_file(filenames,pm2)


    if modes['rm']:
        remove_data_files(filenames)


    return data


def run_cmd(cmd_str, modes):
    if modes['v']:
        p = subprocess.Popen(cmd_str, shell=True, stderr=subprocess.PIPE)
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() != None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
        return None,None,None
    else:
        p = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, shell=True)
         
        ## Talk with date command i.e. read data from stdout and stderr. Store this info in tuple ##
        ## Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.  ##
        ## Wait for process to terminate. The optional input argument should be a string to be sent to the child process, ##
        ## or None, if no data should be sent to the child.
        (output, err) = p.communicate()
         
        ## return status/code
        p_status = p.wait()
        return output, err, p_status




def get_modes(gen_cmds):
    modes = {'rm':True,'no-rm':False,
             'v':False, 'nameX':False,'read':False, 
             'cmd':False, 'extra_data':False}

    if 'v' in gen_cmds:
        modes['v'] = True

    for each in gen_cmds:
        if each in modes:
            modes[each] = True
            dbp("In mode: " + each, modes['v'])
        else:
            raise ValueError("Not recognized in gen_cmd: " + each)
    if modes['no-rm']:
        modes['rm'] = False

    return modes


def check_parameters(pm):
    for each in pm:
        if isinstance(pm[each], int) and each != 'seed' and pm[each]<0:
            raise ValueError("It must be positive or zero: pm['" +each +"'] = "+ str(pm[each]))

    # check seed
    if isinstance(pm['seed'], list):
        if sum(not isinstance(x,int) for x in pm['seed']) > 0:
            raise ValueError("It must be 'auto' or integers: pm['seed'] ")
    else:
        if pm['seed'] != 'auto':
            raise ValueError("It must be 'auto' or integers: pm['seed'] ")
            

    # TODO check neuron_model

    # chcek prog_path
    # find executable
    exec_path = find_exec_path(pm)
    if exec_path == None:
        raise ValueError("No executable available, check pm['prog_path'], is it excutable by this user?")

    # check net
    if isinstance(pm['net'], str):
        if pm['net'].strip() == '-':
            pass # it is OK

        elif not os.access(pm['net'], os.R_OK) :
            if os.access("./network/"+pm['net'],os.R_OK):
                pm['net'] =  "./network/"+pm['net']
            elif os.access("./network/"+pm['net']+'.txt',os.R_OK):
                pm['net'] =  "./network/"+pm['net']+'.txt'
            else:
                raise ValueError("File not exist or not readable: pm['net'] = " + pm['net'])

    elif isinstance(pm['net'], list) :
        if not square_and_only01(pm['net']):
            raise ValueError("If pm['net' is a list, it must be a square matrix with only 0's and 1's")
        # FIXED save it into a file and put the filename as pm['net']
        if not os.path.exists("./network/"):
            os.mkdir("network")
        if os.path.isdir("./network/"):
            net_file_path = get_file_name("./network/net","",pm)
        else:
            net_file_path = get_file_name("./net","",pm)
        save_net(net_file_path,pm['net'])
        pm['net'] = net_file_path
            
    
    # FIXED avoid certain options, such as --isi-path
    # FIXED maybe it is also acceptable
 
def get_cmd_str(pm,modes):
    cmd_str = ''
    if modes['v']:
        cmd_str += ' -v ' # NOT to forget the space
    if modes['read']:
        return ""

    for each in pm:
        if isinstance(pm[each], str) or isinstance(pm[each],unicode):
            if each != 'extra_cmd' and  pm[each] != '' : # Better a warning? TODO
                cmd_str +=  ' --' + each +' '+ pm[each]
            else:
                cmd_str += ' ' + pm['extra_cmd'] + ' '
        elif isinstance(pm[each],int) or isinstance(pm[each], float):
            cmd_str +=  ' --' + each +' '+ str(pm[each])
        elif isinstance(pm[each],list):
            if each == 'prog_path':
                pass # We do not need to handle it
            elif each == 'seed':
                cmd_str +=  ' --' + each +' '+ str(pm[each]).strip('[]').replace(',',' ')
            else:
                raise ValueError("Unrecoginzed value in pm['" + each +"']")
        else:
            raise ValueError("Unrecoginzed value in pm['" + each +"'] with type %s" % type(pm[each]) )
    return cmd_str


def add_exec_and_data_path(pm, cmd_str, exec_path,data_folder,modes):
    cmd_str = exec_path + ' '+cmd_str

    if not os.path.isdir(data_folder) or not os.access(data_folder,os.W_OK):
        dbp("Diractory does not exist to save data files: "+data_folder)
        return -1 # TODO better solu?


    if modes['extra_data']:
        items     = ['volt','isi','ras','conductance','ion-gate']
    else:
        items     = ['volt','isi','ras']

    if not modes['read']:
        filenames = [ [x , get_file_name(data_folder+x,'',pm)] for x in items]
        for each in filenames:
            cmd_str += " --"+each[0] + "-path " + each[1] + " "
    else:
        filenames = [ [x, pm[x+'-path'] ]  for x in items]
        for each in items:
            if not os.access(data_folder+each[1], os.R_OK):
                raise ValueError("You choose mode 'read' but unable to read file: "+ each[0] +" at: " + each[1])

    

    return cmd_str, filenames

def read_data_from_file(filenames,pm):
    print(filenames)
    for each in filenames:
        if not os.access(each[1],os.R_OK):
            dbp("Error, cannot read data files: "+each[1])
        else:
            if each[0] == 'volt':
                # rows = int(pm['t']/pm['stv'])  # CHECK +1 ?
                num_neuron = pm['nE'] + pm['nI']
                data = array.array('B')
                with open(each[1],'rb') as f:
                    while True:
                        try:
                            data.fromfile(f, num_neuron)
                        except EOFError: 
                            break

                data_list = list(data)
                data_mat= [data_list[s:s+num_neuron] for s in xrange(0, len(data_list), num_neuron)]

                each.append(data_mat)
            else:
                with open(each[1],'r') as f:
                    each.append(str_to_matrix(f.read().strip(),'\n','\t'))
    return filenames


def str_to_matrix(string, row_id, col_id):
    rows = string.split(row_id)
    rt = []
    for each in rows:
        rt.append(each.split(col_id))
    return rt

def find_exec_path(pm):
    if isinstance(pm['prog_path'],str):
        pm['prog_path'] = [pm['prog_path']]

    for each in pm['prog_path']:
        if os.path.isfile(each) and os.access(each, os.X_OK): # it is executable
            return each
    return None



def get_file_name(prefix = '', surfix = '', mixstr = ''):
    if surfix and surfix[0] != '.':
        dbp("Warning, no dot(.) in the surfix = " + surfix)
        # We do not automatially 'fix' it

    if mixstr:
        extra = "hash" + str(hash(str(mixstr)))

    return prefix + str(int(time.time()*100)) + extra + surfix




def square_and_only01(mat):
    first_dim_len = len(mat)
    for each in mat:
        if len(each) != first_dim_len:
            return False
        for deeper in each:
            if deeper != 0 and deeper != 1:
                return False
    return True

def save_net(net_file_path,mat):
    
    f = open(net_file_path,"w")
    first_row = True
    for row in mat:
        if not first_row:
            f.write('\n')
        else:
            first_row = False

        first_col = True 
        for one in row:
            if not first_col:
                f.write("  ")
            else:
                first_col = False
            f.write(str(one))
    f.close()

def remove_data_files(filenames):
    for each in filenames:
        try:
            os.remove(each[1])
        except OSError as e:
            dbp("Error occurred when trying to delete temperary files: " + each[1] +  "\nError message: " + e.strerror) 


## A DEMO
##from gen_neu import *
#pm = parameters()
#pm['t'] = 10
#pm['nE'] = 10
#pm['pr'] = 0.4
#pm['ps'] = 0.4
#pm['simulation-method'] = 'SSC'
#result = gen_neu(pm,'v rm')

