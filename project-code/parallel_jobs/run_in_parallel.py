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

    def run_remote_job(self,n_idx,n):
        debug=1
        # for n_idx,n in enumerate(self.config):
        self.current_node = self.config[n]
        self.current_node['node'] = n
        self.current_node['node_idx'] = n_idx
        self.current_node['script_name'] = ntpath.basename(self.current_node['script_path'])
        self.current_node['remote_path'] = self.ssh('cd %s && pwd'%self.current_node['remote_path'])[0]
        if self.current_node['arg_type'].lower() == 'file':
            self.current_node['arg_filename'] = ntpath.basename(self.current_node['arg_file_path'])
        self.current_node['remote_script_path'] = os.path.join(self.current_node['remote_path'], self.current_node['script_name']) #'uname -a > outputfile'

        ## COPY SCRIPT TO REMOTE
        while self.current_node['script_name'] not in self.ssh('ls %s'%self.current_node['remote_path']):
            self.scp(self.current_node['script_path'],
                     '%s:%s' % (self.current_node['hostname'], self.current_node['remote_path']))
            time.sleep(1)
        if debug==1:
            print("script copied")
        self.ssh('chmod +x' , self.current_node['remote_script_path'])
        if debug==1:
            print("chmod +x set")


        ## INPUT
        if self.current_node['arg_type'].lower() == 'params':
            if self.current_node['output_type'].lower() == 'stdout':
                self.remote_pid = self.ssh('nohup %s %s >%s & echo $!'%(self.current_node['remote_script_path'],self.current_node['arg_params'],os.path.join(self.current_node['remote_path'],'outputfile_node_%d' % self.current_node['node_idx'])))
                if debug==1:
                    print("params->stdout ran")
            elif self.current_node['output_type'].lower() == 'file':
                self.remote_pid = self.ssh('nohup %s %s >&- & echo $!'%(self.current_node['remote_script_path'],self.current_node['arg_params']))
                if debug==1:
                    print("params->file ran")
        elif self.current_node['arg_type'].lower() == 'file':
            while ntpath.basename(self.current_node['arg_file_path']) not in self.ssh('ls %s'%self.current_node['remote_path']):
                self.scp(self.current_node['arg_file_path'],'%s:%s' % (self.current_node['hostname'], self.current_node['remote_path']))
                time.sleep(1)
                if debug==1:
                    print("file arg copied ")
            if self.current_node['output_type'].lower() == 'stdout':
                self.remote_pid = self.ssh('nohup %s %s >%s & echo $!'%(self.current_node['remote_script_path'],os.path.join(self.current_node['remote_path'],
                            self.current_node['arg_filename']),os.path.join(self.current_node['remote_path'],
                                                            'outputfile_node_%d' % self.current_node['node_idx'])))
                if debug==1:
                    print("file->stdout ran")

            elif self.current_node['output_type'].lower() == 'file':
                self.remote_pid = self.ssh('nohup %s %s >&- & echo $!'%(self.current_node['remote_script_path'], os.path.join(self.current_node['remote_path'],self.current_node['arg_filename'])))
                if debug==1:
                    print("file->file ran")

        self.remote_pid = self.remote_pid[0]
        print(self.remote_pid)

    def collect_result(self):
        print(self.remote_pid)
        ## Check if output is ready
        self.ps_output = ''
        while self.ps_output is not None:
            self.ps_output = self.ssh('ps', '-ef', '|', 'grep', self.remote_pid, '|', 'grep -v grep')
            time.sleep(2)
        ## OUTPUT
        if self.current_node['output_type'] == 'stdout':
            self.scp('%s:%s' % (self.current_node['hostname'], os.path.join(self.current_node['remote_path'],
                                                                            'outputfile_node_%d' % self.current_node[
                                                                                'node_idx'])),
                     os.path.join(self.current_node['local_output_path'], ''))
        elif self.current_node['output_type'] == 'file':
            self.scp('%s:%s' % (self.current_node['hostname'],
                                os.path.join(self.current_node['remote_path'], self.current_node['output_filename'])),
                     os.path.join(self.current_node['local_output_path'], ''))

    def ssh(self,*args):
        ssh = subprocess.Popen(["ssh", self.current_node['hostname'] , '-F', self.current_node['sshconfigpath'], *args ],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        if result == []:
            error = ssh.stderr.readlines()
            if len(error) > 0:
                print("ERROR in host %s: %s" % (self.current_node['hostname'],error))
            return []
        else:
            return [x.decode('utf-8').strip('\n') for x in result]
        #[0].decode('utf-8')

    def scp(self, *args):
        ssh = subprocess.Popen(["scp", '-F', self.current_node['sshconfigpath'], *args],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        middle_result = ssh.stdout.readlines()
        if middle_result == []:
            error = ssh.stderr.readlines()
            if len(error) > 0:
                print("ERROR in host %s: %s" % (self.current_node['hostname'], error))

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





def run_method_in_parallel(args):
    return args[0].run_remote_job(args[1],args[2])

if __name__ == '__main__':
    parallel_jobs = parallel_runner("config_file.ini")
    all_jobs = [(parallel_jobs,n_idx,n) for n_idx,n in enumerate(parallel_jobs.config)]
    pool = Pool(processes=4)
    pool.map(run_method_in_parallel,all_jobs)
