#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# -----------------------
# Author : jgo
# Execute a perl script into all mailbox newly created,
# on the Dovecot server.
# -----------------------

import subprocess
import os
import re
import logging
from logging.handlers import RotatingFileHandler

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
output = subprocess.check_output(
    'ls -R ' + dest_path + ' | grep "[[:alnum:]]\+@[[:alnum:]]\+" | tr ":" "/" | grep "/"', shell=True)

# Transform the output to a list
output = output.split()
tot_obj = len(output)

global obj
obj = 0

# Execute the script into all dir
try:
    for path in output:
        os.chdir(path)
        logger.info('[Job] - Working on %s' % path)
        result = subprocess.call(init_path + script_path, shell=True)
        if result == 1 :
            obj += 1
except SyntaxError:
    logger.error('SyntaxError, your target already exists.')
    print 'Please check your log file SyntaxError detected'
except OSError:
    logger.error('OSError, this script can\'t be used on files')
    print 'Please check your log file OSError detected'
finally:
    os.chdir(init_path)

    # Regex to get the domains :
    with open(logfile, 'r') as f:
        data = f.read()
    f.close()
    
    mails = re.findall(r'[\w\.-]+@[\w\.-]+', data, re.M|re.I)
    domains = re.findall(r'@([\w\.-]+)', data)

    domains = list(set(domains))
    mails = list(set(mails))

    with open(logfile, 'a') as f:
        f.write("E-mails who has been converted :\n")
        for mail in mails:
            f.write(mail + "\n")
            f.write("\n" + "\n")

        f.write("Domains who has been converted :\n")
        for domain in domains:
            f.write(domain +"\n")
            f.write("\n" + "\n")
    f.close()

    print '------------------------------------'
    print 'Impacted domains : \n', domains
    print '------------------------------------'
    print 'Impacted e-mails : \n', mails
    print 'Number of directories parsed : %d / %d' % (obj, tot_obj)
    print 'Log file : %s' % logfile
    print '===================================================='