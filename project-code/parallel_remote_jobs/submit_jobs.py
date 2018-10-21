#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 00:23:36 2018

@author: Vafa
"""

from configobj import ConfigObj,ConfigObjError
from multiprocessing import Pool, Manager
import subprocess
import os
import ntpath
import time
import argparse
import sys
import pickle
from datetime import datetime

#TODO cleanup remote
#TODO suffix for each file
#TODO multiple output files

class run_in_parallel:
    def __init__(self,config_path,output_suffix,debug_run = False):
        self.debug_run = debug_run
        self.config_validator(config_path)
        self.all_pids = []
        self.output_suffix = output_suffix
        for n_idx, n in enumerate(self.config):
            self.config[n]['node'] = n
            self.config[n]['node_idx'] = n_idx
            self.config[n]['script_name'] = ntpath.basename(self.config[n]['script_path'])
            self.config[n]['remote_path'] = self.ssh(n, 'cd %s && pwd' % self.config[n]['remote_path'])[0]
            if self.config[n]['arg_type'].lower() == 'file':
                self.config[n]['arg_filename'] = ntpath.basename(self.config[n]['arg_file_path'])
            self.config[n]['remote_script_path'] = os.path.join(self.config[n]['remote_path'], self.config[n]['script_name'])
            if not os.path.exists(self.config[n]['local_output_path']):
                os.makedirs(self.config[n]['local_output_path'])

    def run_remote_job(self,n_idx,n, all_pids):
        ## COPY SCRIPT TO REMOTE
        while self.config[n]['script_name'] not in self.ssh(n,'ls %s'%self.config[n]['remote_path']):
            self.scp(n,self.config[n]['script_path'],'%s:%s' % (self.config[n]['hostname'], self.config[n]['remote_path']))
            time.sleep(1)
        if self.debug_run:
            print("script copied")
        self.ssh(n,'chmod +x' , self.config[n]['remote_script_path'])
        if self.debug_run:
            print("chmod +x set")

        ## COPY INPUT TO REMOTE AND RUN
        if self.config[n]['arg_type'].lower() == 'params+file':
            while ntpath.basename(self.config[n]['arg_file_path']) not in self.ssh(n, 'ls %s' % self.config[n][
                'remote_path']):
                self.scp(n, self.config[n]['arg_file_path'],
                         '%s:%s' % (self.config[n]['hostname'], self.config[n]['remote_path']))
                time.sleep(1)
        if self.config[n]['output_type'].lower() in ['stdout','stdout+file']:
            self.remote_pid = self.ssh(n,'nohup %s %s >%s & echo $!'%(self.config[n]['remote_script_path'],self.config[n]['arg_params'],os.path.join(self.config[n]['remote_path'],'outputfile_node_%d' % self.config[n]['node_idx'])))
            if self.debug_run:
                print("params->stdout ran")
        elif self.config[n]['output_type'].lower() == 'file':
            self.remote_pid = self.ssh(n,'nohup %s %s >&- & echo $!'%(self.config[n]['remote_script_path'],self.config[n]['arg_params']))
            if self.debug_run:
                print("params->file ran")

        self.remote_pid = self.remote_pid[0]
        all_pids.append((n,self.remote_pid))
        print('Remote Pid on %s: %s'%(self.config[n]['node'],self.remote_pid))



    def collect_result(self,n_idx,n,all_pids):
        self.ps_output = self.ssh(n,'ps', '-ef', '|', 'grep', self.config[n]['pid'], '|', 'grep -v grep')
        if len(self.ps_output) == 0 :
            if self.config[n]['output_type'] == 'stdout':
                self.scp(n,'%s:%s' % (self.config[n]['hostname'], os.path.join(self.config[n]['remote_path'],'outputfile_node_%d' % (n_idx))),os.path.join(self.config[n]['local_output_path'], ''))
            elif self.config[n]['output_type'] == 'file':
                # file_name, file_extension = os.path.splitext(self.config[n]['output_filename'])
                self.scp(n,'%s:%s' % (self.config[n]['hostname'],os.path.join(self.config[n]['remote_path'], self.config[n]['output_filename'])),os.path.join(self.config[n]['local_output_path'], ''))
            elif self.config[n]['output_type'] == 'stdout+file':
                self.scp(n, '%s:%s' % (self.config[n]['hostname'],
                                       os.path.join(self.config[n]['remote_path'], 'outputfile_node_%d' % (n_idx))),
                         os.path.join(self.config[n]['local_output_path'], ''))
                self.scp(n, '%s:%s' % (self.config[n]['hostname'],
                                       os.path.join(self.config[n]['remote_path'], self.config[n]['output_filename'])),
                         os.path.join(self.config[n]['local_output_path'], ''))
            all_pids.remove((n, self.config[n]['pid']))
            print("Results from %s collected"%n)



    def ssh(self,*args):
        n = args[0]
        args = args[1:]
        ssh = subprocess.Popen(["ssh", self.config[n]['hostname'] , '-F', self.config[n]['sshconfigpath'], *args ],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            error = ssh.stderr.readlines()
            if len(error) > 0:
                print("ERROR in host %s: %s" % (self.config[n]['hostname'],error))
            return []
        else:
            return [x.decode('utf-8').strip('\n') for x in result]

    def scp(self, *args):
        n = args[0]
        args = args[1:]
        ssh = subprocess.Popen(["scp", '-F', self.config[n]['sshconfigpath'], *args],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        middle_result = ssh.stdout.readlines()
        if middle_result == []:
            error = ssh.stderr.readlines()
            if len(error) > 0:
                print("ERROR in host %s: %s" % (self.config[n]['hostname'], error))

    def config_validator(self,config_path):
        self.config_path = config_path
        try:
            self.config = ConfigObj(self.config_path)
        except ConfigObjError:
            raise ValueError("Config file cannot be parsed, make sure there is no duplicates in the top level node names")
        for n_idx, n in enumerate(self.config):
            if 'hostname' not in self.config[n].keys():
                raise ValueError("%s: 'hostname' keyword is missing"%n)
            if 'sshconfigpath' not in self.config[n].keys():
                raise ValueError("%s: 'sshconfigpath' keyword is missing" % n)
            if not os.path.isfile(self.config[n]['sshconfigpath']):
                raise ValueError("%s: The ssh config file %s does not exists" % (n,self.config[n]['sshconfigpath']))
            if 'script_path' not in self.config[n].keys():
                raise ValueError("%s: 'script_path' keyword is missing" % n)
            if not os.path.isfile(self.config[n]['script_path']):
                raise ValueError("%s: The script file %s does not exists" % (n, self.config[n]['script_path']))
            if 'remote_path' not in self.config[n].keys():
                raise ValueError("%s: 'remote_path' keyword is missing" % n)
            if 'arg_type' not in self.config[n].keys():
                raise ValueError("%s: 'arg_type' keyword is missing" % n)

            if self.config[n]['arg_type'] == 'params':
                if 'arg_params' not in self.config[n].keys():
                    raise ValueError("%s: 'arg_type' is defined as params, but 'arg_params' keyword is missing" % n)
            elif self.config[n]['arg_type'] == 'params+file':
                if 'arg_params' not in self.config[n].keys():
                    raise ValueError("%s: 'arg_type' is defined as params+file, in this case the 'arg_params' is also needed but 'arg_params' keyword is missing" % n)
                if 'arg_file_path' not in self.config[n].keys():
                    raise ValueError("%s: arg_type is defined as file, but 'arg_file_path' keyword is missing" % n)
                if not os.path.isfile(self.config[n]['arg_file_path']):
                    raise ValueError("%s: The arg file %s does not exists" % (n, self.config[n]['arg_file_path']))
            if 'output_type' not in self.config[n].keys():
                raise ValueError("%s: 'output_type' keyword is missing" % n)
            if self.config[n]['output_type'] in ['file' ,'stdout+file'] :
                if 'output_filename' not in self.config[n].keys():
                    raise ValueError("%s: 'output_type' is defined as file, but 'output_filename' keyword is missing" % n)
            if 'local_output_path' not in self.config[n].keys():
                raise ValueError("%s: 'local_output_path' keyword is missing" % n)

    def sync_pids_with_config(self):
        for item in self.all_pids:
            self.config[item[0]]['pid'] = item[1]
            # self.config[item[0]]['results_collected'] = False


def run_method_in_parallel(args):
    return args[0].run_remote_job(args[1],args[2],args[3])

def collect_results_in_parallel(args):
    return args[0].collect_result(args[1],args[2],args[3])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Running remote parallel jobs',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('ConfPath', metavar='ConfPath', type=str, nargs=1,
                        help='Path of configuration file')

    parser.add_argument('ProcNum', metavar='ProcNum', type=int, nargs=1,
                        help='Number of processes')

    parser.add_argument('--CProcNum', metavar='Num', type=int, nargs=1,default=1,
                        help='Number of processes used for collecting the results.')

    suffix = '_' + str(datetime.now()).replace('-', '').replace(' ', '_').replace(':', '')[
                        0:str(datetime.now()).replace('-', '').replace(' ', '_').replace(':', '').index(
                            '.') + 3].replace('.', '')

    parser.add_argument('--suffix', metavar='suffix', type=str, nargs=1,default=suffix,
                        help='suffix to be added to output file names.')

    parser.add_argument('--nometa', help='If used, the metadata will not be saved (warning: results cannot be collected later).', action='store_true')


    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    config_path = args.ConfPath[0]
    process_num_submit = args.ProcNum[0]
    process_num_collect = args.CProcNum[0] if type(args.CProcNum) == list else args.CProcNum
    output_suffix = args.suffix[0] if  type(args.suffix) == list else args.suffix
    nometa = args.nometa
    # print(args)
    # sys.exit()
    all_pids = Manager().list()
    parallel_jobs = run_in_parallel(config_path,output_suffix)
    all_jobs = [(parallel_jobs,n_idx,n, all_pids) for n_idx,n in enumerate(parallel_jobs.config)]
    pool = Pool(processes=process_num_submit)
    pool.map(run_method_in_parallel,all_jobs)
    parallel_jobs.all_pids = all_pids

    if not nometa:
        if not os.path.exists('./metadata'):
            os.makedirs('./metadata')
        pickle.dump(all_pids, open(os.path.join('./metadata','md' + suffix + '.pkl'), "wb"))

    parallel_jobs.sync_pids_with_config()
    pool = Pool(processes=process_num_collect)
    print("collecting results")
    while len(all_pids)> 0 :
        time.sleep(3)
        all_running_jobs = [(parallel_jobs, n_idx, n, all_pids) for n_idx, n in enumerate(parallel_jobs.config) if (n,parallel_jobs.config[n]['pid']) in all_pids]
        pool.map(collect_results_in_parallel, all_running_jobs)
        print ("waiting for other results...")

    print("All of the remote results collected")