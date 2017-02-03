#!/usr/bin/python3

import sys, time, os
import subprocess
from subprocess import Popen, PIPE, run
from threading import Thread
import json

colors = {
    'fg': '#c8c8c8',
    'bg': '#282828',
    'fg-dim': '#777777',
    'bg-light': '#888888',
    'fg-dark': '#000000',
    'green': '#b5bd68',
    'purple': '#b294bb',
    'blue': '#81a2be',
    'cyan': '#8abeb7',
    'orange': '#de935f',
    'yellow': '#f0c674'
}
bmargin = 6
bpadding = 5

ws_aliases = {
    'home': {
        '1': 'shell',
        '2': 'media',
        '3': 'web',
        '4': 'work'
    },
    'sysrev': {
        '1': 'web',
        '2': 'server',
        '3': 'client',
        '4': 'shell',
        '5': 'shell'
    },
    'i3': {
        '1': 'shell',
        '2': 'emacs'
    }
}

def get_ws_alias(wname):
    pname = cache['active_project'][1:]
    if pname in ws_aliases.keys():
        if wname in ws_aliases[pname].keys():
            return ws_aliases[pname][wname]
    return None

def write_icon(s):
    return ('%{T2}' + s + '%{T-}')

def write_offset(offset):
    return ('%{O' + str(offset) + '}')

def write_spaces(nspaces):
    if nspaces > 0:
        return ('%{T1}' + (' '*nspaces) + '%{T-}')
    else:
        return ''

def write_simple_block(label, color, val_color, width, val):
    nspaces = width - len(val)
    return ('%{U' + colors[color] + '}' +
            '%{F' + colors[color] + '}' +
            '%{+u}' +
            write_offset(bpadding) +
            '' + label + ' ' + write_spaces(nspaces) +
            '%{F' + colors[val_color] + '}' + val +
            write_offset(bpadding) +
            '%{-u}' +
            write_offset(bmargin))

def write_multi_block(color, sections):
    s = ''
    s += '%{U' + colors[color] + '}' + '%{+u}'
    s += write_offset(bpadding)
    for section in sections:
        [scolor, sval, swidth] = section
        s += '%{F' + colors[scolor] + '}'
        nspaces = swidth - len(sval)
        s += write_spaces(nspaces)
        s += sval
    s += write_offset(bpadding)
    s += '%{-u}'
    s += write_offset(bmargin)
    return s

cache = {
    'active_project': '',
    'i3_ws': {
        'result': '',
        'lemonbar': ''},
    'values': {
        'qemu': '',
        'synergy': '',
        'cpu': '',
        'diskio': '',
        'netspeed': '',
        'fsusage': '',
        'btcprice': '',
        'volume': '',
        'packages': '',
        'date': '',
        'time': '',
        'battery': ''
    },
    'blocks': {
        'qemu': '',
        'synergy': '',
        'cpu': '',
        'diskio': '',
        'netspeed': '',
        'fsusage': '',
        'btcprice': '',
        'volume': '',
        'packages': '',
        'date': '',
        'time': '',
        'battery': ''
    },
    'main': '',
    'output': '',
    'current': ''
}

def get_packages_status():
    p = Popen(["check-packages.sh"], shell=True, encoding='utf8', stdout=PIPE)
    result = p.communicate()[0].strip()
    return result

def get_volume():
    p = Popen(["pamixer", "--get-volume"], encoding='utf8', stdout=PIPE)
    result = p.communicate()[0].strip()
    return result

def qemu_status():
    p = Popen(['qemu-status win10'], shell=True, encoding='utf8', stdout=PIPE)
    result = p.communicate()[0].strip()
    if result == 'on':
        return True
    else:
        return False

def synergy_status():
    p = Popen(['user-service-status synergys'], shell=True, encoding='utf8', stdout=PIPE)
    result = p.communicate()[0].strip()
    if result == 'on':
        return True
    else:
        return False

def i3_msg(mtype, marg):
    p = Popen(['i3-msg -t %s %s' % (mtype, marg)],
              shell=True, encoding='utf8', stdout=PIPE)
    result = p.communicate()[0].strip()
    return result
    
def i3_get_workspaces():
    return i3_msg('get_workspaces', '')

def write_main_output():
    s = ''
    blocks = ['qemu',
              'synergy',
              'cpu',
              'diskio',
              'netspeed',
              'fsusage',
              'btcprice',
              'volume',
              'battery',
              'packages',
              'date',
              'time']
    for name in blocks:
        s += cache['blocks'][name]
    return s

def write_full_output():
    return ''.join(
        ['%{l}',
         cache['i3_ws']['lemonbar'],
         '%{r}',
         cache['main']]
    )

def update_main_output():
    cache['main'] = write_main_output()
    
def update_output():
    cache['output'] = write_full_output()

def update_output_all():
    update_main_output()
    update_output()

def render_block(name, vals):
    if name == 'qemu':
        status = vals
        if status == True:
            icon = ''
            color = 'green'
        else:
            icon = ''
            color = 'fg-dim'
        return write_multi_block(
            color,
            [[color, write_icon(icon), 0],
             ['fg', ' qemu', 0]]
        )
    elif name == 'synergy':
        status = vals
        if status == True:
            icon = ''
            color = 'green'
        else:
            icon = ''
            color = 'fg-dim'
        return write_multi_block(
            color,
            [[color, write_icon(icon), 0],
             ['fg', ' synergy', 0]]
        )
    elif name == 'cpu':
        cpu = vals
        return write_simple_block(
            write_icon(''),
            'green', 'fg', 4, '%s%%' % cpu)
    elif name == 'diskio':
        [diskread, diskwrite] = vals
        return write_multi_block(
            'cyan',
            [['cyan', write_icon(''), 0],
             ['fg', diskread, 7],
             ['cyan', ' ' + write_icon(''), 0],
             ['fg', diskwrite, 7],
             ['cyan', ' ' + write_icon(''), 0]]
        )
    elif name == 'netspeed':
        [netdown, netup] = vals
        return write_multi_block(
            'blue',
            [['blue', write_icon(''), 0],
             ['fg', netdown, 7],
             ['blue', ' ' + write_icon(''), 0],
             ['fg', netup, 7],
             ['blue', ' ' + write_icon(''), 0]]
        )
    elif name == 'fsusage':
        [fsused, fssize] = vals
        return write_multi_block(
            'purple',
            [['purple', write_icon(''), 0],
             ['fg', ' ' + fsused, 0],
             ['purple', ' /', 0],
             ['fg', fssize, 0]]
        )
    elif name == 'btcprice':
        btcprice = vals
        return write_simple_block(
            write_icon(''),
            'green', 'fg', 4, btcprice)
    elif name == 'volume':
        volume = vals
        return write_simple_block(
            write_icon(''),
            'orange', 'fg', 4, volume+'%')
    elif name == 'packages':
        pstatus = vals
        return write_simple_block(
            write_icon(''), 'cyan', 'fg', 3, pstatus)
    elif name == 'date':
        datestr = vals
        return write_simple_block(
            write_icon(''), 'blue', 'fg', 10, datestr)
    elif name == 'time':
        timestr = vals
        return write_simple_block(
            write_icon(''), 'purple', 'fg', 8, timestr)
    elif name == 'battery':
        percent = vals
        return write_simple_block(
            write_icon(''), 'yellow', 'fg', 4, percent+'%'
        )
    else:
        return ''

def update_block(name, vals, redraw=False):
    prev = cache['values'][name]
    if prev != vals:
        cache['values'][name] = vals
        cache['blocks'][name] = render_block(name, vals)
        if redraw:
            update_output_all()

def update_from_conky(conkyline):
    [cpu, memused, memmax, diskread, diskwrite, netdown, netup,
     fsused, fssize, datestr, timestr, battery] = (
        conkyline.strip().split(';')
    )
    update_block('cpu', cpu)
    update_block('diskio', [diskread, diskwrite])
    update_block('netspeed', [netdown, netup])
    update_block('fsusage', [fsused, fssize])
    update_block('date', datestr)
    update_block('time', timestr)
    update_block('battery', battery)

ck = Popen(['conky -c ~/.i3/conky/conkyrc_raw'], shell=True, encoding='utf8', stdout=PIPE)
lb = subprocess.Popen(["lemonbar -g 3840x55 -o 0 -u 2 -B" + colors['bg'] + " -f 'sauce code pro medium:size=12' -f 'fontawesome:size=13'"], shell=True, encoding='utf8', stdin=PIPE)

def get_active_project():
    return open(os.path.expanduser('~/i3pwsvar')).readlines()[0].strip()

def update_active_project():
    cache['active_project'] = get_active_project()

def ws_order(ws):
    wname = '_'.join(ws['name'].split('_')[1:])
    if wname[:2] == '10':
        return 10
    else:
        return int(wname[0])

def write_project_block(name, active, wscount):
    if active:
        fg = colors['fg-dark']
        bg = colors['bg-light']
    else:
        fg = colors['fg-dim']
        bg = colors['bg']
    s = ''
    s += '%{-u}'
    s += '%{F' + fg + '}'
    s += '%{B' + bg + '}'
    s += write_offset(bpadding)
    if active:
        s += name
    else:
        s += name[:1]
    if not active:
        s += '[%d]' % wscount
    s += write_offset(bpadding)
    s += '%{B-}%{F-}'
    s += write_offset(bmargin)
    return s

def write_projects_section(all_ws):
    pactive = cache['active_project'][1:]
    
    pnames = []
    for ws in all_ws:
        pname = ws['name'].split('_')[0][1:]
        if pname not in pnames:
            pnames += [pname]
            
    pcounts = {}
    for pname in pnames:
        pcounts[pname] = 0
    for ws in all_ws:
        pname = ws['name'].split('_')[0][1:]
        pcounts[pname] += 1
    
    s = ''
    s += '%{-u}'
    for name in pnames:
        if name != pactive:
            s += write_project_block(name, False, pcounts[name])
    s += write_project_block(pactive, True, pcounts[pactive])
    return s
    
def update_workspaces(all_ws_str):
    update = False

    prev_active = cache['active_project']
    update_active_project()
    if prev_active != cache['active_project']:
        update = True
        
    if cache['i3_ws']['result'] != all_ws_str:
        update = True
        cache['i3_ws']['result'] = all_ws_str

    if update:
        s = ''
        try:
            all_ws = json.loads(all_ws_str)
        except:
            all_ws = []
        pactive = cache['active_project'][1:]
        s += write_projects_section(all_ws)
        s += write_offset(bmargin)
        all_ws_sorted = sorted(all_ws, key=ws_order)
        for ws in all_ws_sorted:
            raw_name = ws['name']
            pname = ws['name'].split('_')[0][1:]
            wname = '_'.join(ws['name'].split('_')[1:])
            walias = get_ws_alias(wname)
            if walias == None:
                wdisplay = wname
            else:
                wdisplay = wname + '[' + walias + ']'
            wactive = (pname == pactive)
            if wactive:
                color = {True: 'fg', False: 'fg-dim'}[ws['visible']]
                s += write_multi_block(
                    color,
                    [[color, wdisplay, 0]]
                )
        cache['i3_ws']['lemonbar'] = s
        update_output()

class i3ws_Thread(Thread):
    def run(self):
        while True:
            update_workspaces( i3_get_workspaces() )
            time.sleep(0.05)

class conky_Thread(Thread):
    def run(self):
        while True:
            result = str(ck.stdout.readline())
            update_from_conky(result)
            update_output_all()

class volume_Thread(Thread):
    def run(self):
        while True:
            update_block('volume', get_volume(), True)
            time.sleep(0.1)

class output_Thread(Thread):
    def run(self):
        while True:
            if cache['output'] != cache['current']:
                print(cache['output'], end='\n', file=lb.stdin)
                lb.stdin.flush()
                cache['current'] = cache['output']
            time.sleep(0.05)

class misc_Thread(Thread):
    def run(self):
        while True:
            update_block('qemu', qemu_status(), True)
            update_block('synergy', synergy_status(), True)
            time.sleep(0.5)

class packages_Thread(Thread):
    def run(self):
        while True:
            update_block('packages', get_packages_status(), True)
            time.sleep(120)

update_active_project()

i3ws = i3ws_Thread()
i3ws.start()

conky = conky_Thread()
conky.start()

volume = volume_Thread()
volume.start()

packages = packages_Thread()
packages.start()

misc = misc_Thread()
misc.start()

output = output_Thread()
output.start()

output.join()
