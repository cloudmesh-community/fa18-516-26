from configobj import ConfigObj
import multiprocessing
import subprocess
import sys
import argparse
import os
import json

config = ConfigObj("config_file.ini")
command = 'uname -a > outputfile'
results = {}
if not os.path.exists('results'):
    os.makedirs('results')
for n_idx,n in enumerate(config):
    node = config[n]
    host = node['hostname']
    sshconfigpath = node['sshconfigpath']
    expected_results = node['expected_result']
    if expected_results.lower() == 'stdout':
        ssh = subprocess.Popen(["ssh", host , '-F',sshconfigpath , command],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        middle_result = ssh.stdout.readlines()
        if middle_result == []:
            error = ssh.stderr.readlines()
            print ("ERROR: %s" % error)
        else:
            results[host] = middle_result[0].decode('utf-8').strip('\n')
    elif expected_results.lower() == 'file':
        ssh = subprocess.Popen(["ssh", host, '-F', sshconfigpath, command],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        ssh = subprocess.Popen(["scp", '-F', sshconfigpath, '%s:outputfile' %host, 'results/outputfile%d'%n_idx],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        middle_result = ssh.stdout.readlines()
        if middle_result == []:
            error = ssh.stderr.readlines()
            print("ERROR: %s" % error)
        else:
            results[host] = middle_result[0].decode('utf-8').strip('\n')
print(results)
with open(os.path.join('results', 'stdout.json'), 'w') as file:
    json.dump(results,file,sort_keys=True,indent=3)
