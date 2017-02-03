#!/bin/python3
import sys, os
from subprocess import Popen, PIPE
import json

def get_last_project():
    return open(os.path.expanduser('~/i3pwslast')).readlines()[0].strip()

def i3_msg(mtype, marg):
    p = Popen(['i3-msg -t %s %s' % (mtype, marg)],
              shell=True, encoding='utf8', stdout=PIPE)
    result = p.communicate()[0].strip()
    return result
    
def i3_get_workspaces():
    return i3_msg('get_workspaces', '')

all_ws = json.loads(i3_get_workspaces())

active_ws = None
for ws in all_ws:
    if ws['visible']:
        active_ws = ws
        break

def ws_order(ws):
    wname = '_'.join(ws['name'].split('_')[1:])
    if wname[:2] == '10':
        return 10
    else:
        return int(wname[0])

pname = get_last_project()

if active_ws != None and pname != None:
    wname = pname + '_' + str(ws_order(active_ws))
    i3_msg('command',
           'move container to workspace ' + wname)
