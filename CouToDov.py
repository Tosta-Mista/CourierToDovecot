#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# -----------------------
# Author : jgo
# Execute a perl script into all mailbox newly created,
# on the Dovecot server.
# -----------------------
__author__ = 'jgo'
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import os
import re
import Queue
import threading

## [Config VARS] --------------------------------------------
# Don't change this value! :)
init_path = os.path.dirname(os.path.realpath(__file__))
# Change this value with your target dir (example : '/var/spool/mail')
dest_path = '/var/spool/mail/'
# Change this value with your script path (example: '/script.sh')
script_path = '/courier-dovecot-migrate.pl --to-dovecot --convert --recursive'
# Naem of the logfile
logfile = 'valhalla.log'
## ----------------------------------------------------------
# Cleaning old log file :
subprocess.call('rm -rf ' + init_path + "/" + logfile, shell=True)

## [Logging] ------------------------------------------------
# Create logger object used to write logfile
logger = logging.getLogger()

# Set your Log level to debug => Write everything
logger.setLevel(logging.DEBUG)

# Choose how you want your log format
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

# Create a file (valhalla.log) in "append mode", max size => 30Mb
# and 1 backup.
file_handler = RotatingFileHandler(logfile, 'a', 30000000, 1)

# Assign our formatter and set to debug mode.
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Create a second handler to display the log on the console
steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
logger.addHandler(steam_handler)
## ----------------------------------------------------------

print '===================================================='
print '[SCRIPT STATUS]'
print '===================================================='

# Create a list with all directory
folderList = []
for root, subFolder, files in os.walk(init_path+dest_path):
    for folder in subFolder:
        folderList.append(os.path.join(root, folder))

tot_obj = len(folderList)

#load up a queue with your data, this will handle locking
q = Queue.Queue()
for path in folderList:
    q.put(path)


def get_domains(init_path, logfile):
    # Regex to get the domains :
    with open(init_path+"/"+logfile, 'r') as f:
        data = f.read()
    f.close()

    mails = re.findall(r'[\w\.-]+@[\w\.-]+', data, re.M | re.I)
    domains = re.findall(r'@([\w\.-]+)', data)

    # Put into a set to sort my data
    domains = list(set(domains))
    mails = list(set(mails))

    with open(init_path+"/"+logfile, 'a') as f:
        f.write("------------------------------------------------------------------------\n")
        f.write("E-mails who has been converted :\n")
        for mail in mails:
            f.write(mail + "\n")

        f.write("\n")

        f.write("Domains who has been converted :\n")
        for domain in domains:
            f.write(domain + "\n")

    f.close()

    print """---------------------------------------
Impacted e-mails : %s
---------------------------------------
Impacted domains : %s
Number of directories parsed : %d / %d'
Log file : %s'
====================================================""" % (mails, domains, obj, tot_obj, logfile)


#define a worker function
def worker(queue):
    global obj
    obj = 0
    queue_full = True
    while queue_full:
        try:
            #get your data off the queue, and do some work
            path = queue.get(False)
            os.chdir(path)
            logger.info('[Job] - Working on %s' % path)
            result = subprocess.call(init_path + script_path, shell=True)
            q.task_done()
            if result == 1:
                obj += 1

        except Queue.Empty:
            queue_full = False


#create as many threads as you want
thread_count = 10
print '*** Main thread waiting'
for i in range(thread_count):
    t = threading.Thread(target=worker, args=(q,))
    t.start()

q.join()
get_domains(init_path, logfile)
print '*** Done'

