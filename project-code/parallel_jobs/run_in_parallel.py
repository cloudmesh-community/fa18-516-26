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
import shlex


class parallel_runner:
    def __init__(self,config_path):
        self.config_validator(config_path)
        if not os.path.exists('output'):
            os.makedirs('output')
        self.all_pids = []
    def run_remote_job(self,n_idx,n, all_pids):
        debug=0
        # for n_idx,n in enumerate(self.config):
        self.config[n]['node'] = n
        self.config[n]['node_idx'] = n_idx
        self.config[n]['script_name'] = ntpath.basename(self.config[n]['script_path'])
        self.config[n]['remote_path'] = self.ssh(n,'cd %s && pwd'%self.config[n]['remote_path'])[0]
        if self.config[n]['arg_type'].lower() == 'file':
            self.config[n]['arg_filename'] = ntpath.basename(self.config[n]['arg_file_path'])
        self.config[n]['remote_script_path'] = os.path.join(self.config[n]['remote_path'], self.config[n]['script_name']) #'uname -a > outputfile'

        ## COPY SCRIPT TO REMOTE
        while self.config[n]['script_name'] not in self.ssh(n,'ls %s'%self.config[n]['remote_path']):
            self.scp(n,self.config[n]['script_path'],'%s:%s' % (self.config[n]['hostname'], self.config[n]['remote_path']))
            time.sleep(1)
        if debug==1:
            print("script copied")
        self.ssh(n,'chmod +x' , self.config[n]['remote_script_path'])
        if debug==1:
            print("chmod +x set")


        ## INPUT
        if self.config[n]['arg_type'].lower() == 'params':
            if self.config[n]['output_type'].lower() == 'stdout':
                self.remote_pid = self.ssh(n,'nohup %s %s >%s & echo $!'%(self.config[n]['remote_script_path'],self.config[n]['arg_params'],os.path.join(self.config[n]['remote_path'],'outputfile_node_%d' % self.config[n]['node_idx'])))
                if debug==1:
                    print("params->stdout ran")
            elif self.config[n]['output_type'].lower() == 'file':
                self.remote_pid = self.ssh(n,'nohup %s %s >&- & echo $!'%(self.config[n]['remote_script_path'],self.config[n]['arg_params']))
                if debug==1:
                    print("params->file ran")
        elif self.config[n]['arg_type'].lower() == 'file':
            while ntpath.basename(self.config[n]['arg_file_path']) not in self.ssh(n,'ls %s'%self.config[n]['remote_path']):
                self.scp(n,self.config[n]['arg_file_path'],'%s:%s' % (self.config[n]['hostname'], self.config[n]['remote_path']))
                time.sleep(1)
                if debug==1:
                    print("file arg copied ")
            if self.config[n]['output_type'].lower() == 'stdout':
                self.remote_pid = self.ssh(n,'nohup %s %s >%s & echo $!'%(self.config[n]['remote_script_path'],os.path.join(self.config[n]['remote_path'],
                            self.config[n]['arg_filename']),os.path.join(self.config[n]['remote_path'],
                                                            'outputfile_node_%d' % self.config[n]['node_idx'])))
                if debug==1:
                    print("file->stdout ran")

            elif self.config[n]['output_type'].lower() == 'file':
                self.remote_pid = self.ssh(n,'nohup %s %s >&- & echo $!'%(self.config[n]['remote_script_path'], os.path.join(self.config[n]['remote_path'],self.config[n]['arg_filename'])))
                if debug==1:
                    print("file->file ran")

        self.remote_pid = self.remote_pid[0]
        all_pids.append((n,self.remote_pid))
        print(self.remote_pid)

    def collect_result(self,n_idx,n,all_pids):
        # if  self.config[n]['results_collected'] == False:
        self.ps_output = self.ssh(n,'ps', '-ef', '|', 'grep', self.config[n]['pid'], '|', 'grep -v grep')
        ## OUTPUT
        #self.ps_output is not None and
        if len(self.ps_output) == 0 :
            if self.config[n]['output_type'] == 'stdout':
                self.scp(n,'%s:%s' % (self.config[n]['hostname'], os.path.join(self.config[n]['remote_path'],'outputfile_node_%d' % n_idx)),os.path.join(self.config[n]['local_output_path'], ''))
            elif self.config[n]['output_type'] == 'file':
                self.scp(n,'%s:%s' % (self.config[n]['hostname'],os.path.join(self.config[n]['remote_path'], self.config[n]['output_filename'])),os.path.join(self.config[n]['local_output_path'], ''))
            all_pids.remove((n, self.config[n]['pid']))
            print("Results from node %s collected"%n)
            # self.config[n]['results_collected'] = True
        # else:
        #     time.sleep(3)



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
            if self.config[n]['arg_type'] == 'file':
                if 'arg_file_path' not in self.config[n].keys():
                    raise ValueError("%s: arg_type is defined as file, but 'arg_file_path' keyword is missing" % n)
                if not os.path.isfile(self.config[n]['arg_file_path']):
                    raise ValueError("%s: The arg file %s does not exists" % (n, self.config[n]['arg_file_path']))
            elif self.config[n]['arg_type'] == 'params':
                if 'arg_params' not in self.config[n].keys():
                    raise ValueError("%s: 'arg_type' is defined as params, but 'arg_params' keyword is missing" % n)
            if 'output_type' not in self.config[n].keys():
                raise ValueError("%s: 'output_type' keyword is missing" % n)
            if self.config[n]['output_type'] == 'file':
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
    all_pids = Manager().list()
    parallel_jobs = parallel_runner("config_file.ini")
    all_jobs = [(parallel_jobs,n_idx,n, all_pids) for n_idx,n in enumerate(parallel_jobs.config)]
    pool = Pool(processes=4)
    pool.map(run_method_in_parallel,all_jobs)
    parallel_jobs.all_pids = all_pids
    parallel_jobs.sync_pids_with_config()
    print("collecting results")
    while len(all_pids)> 0 :
        all_running_jobs = [(parallel_jobs, n_idx, n, all_pids) for n_idx, n in enumerate(parallel_jobs.config) if (n,parallel_jobs.config[n]['pid']) in all_pids]
        pool.map(collect_results_in_parallel, all_running_jobs)
        print ("waiting for other results...")
        time.sleep(3)
    # print(parallel_jobs.config)
