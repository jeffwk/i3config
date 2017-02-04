#!/usr/bin/python3

import sys, time, os
import subprocess
from subprocess import Popen, PIPE, run
from threading import Thread
import json
import argparse

def write_to_file(str,path):
    f = open(path,'w')
    print(str, end='\n', file=f)
    f.close()

def json_to_file(j,path):
    str = json.dumps(j)
    write_to_file(str,path)

def json_from_file(path):
    f = open(path,'r')
    return json.load(f)
    
basedir = os.path.expanduser('~/.i3/i3proj')

def i3path(relpath):
    return '%s/%s' % (basedir, relpath)

def i3p_path(relpath):
    return os.path.expanduser('~/.i3/i3proj/%s' % fname)

class i3p_Config:
    def __init__(self,margin,padding,colors):
        self.margin = margin
        self.padding = padding
        self.colors = colors

default_config = i3p_Config(
    margin=6,
    padding=5,
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
)

def check_pname(pname):
    return (type(pname) == str)

def check_wname(wname):
    return (type(wname) == str)

def is_str(x):
    return (type(x) == str)

class i3p_Util:
    def __init__(self):
        pass
    
    def rofi_select(self, options, message):
        p = Popen(['rofi', '-dmenu', '-mesg', message],
                  encoding='utf8', stdin=PIPE, stdout=PIPE)
        print('\n'.join(options), end='\n', file=p.stdin)
        p.stdin.flush()
        result = p.communicate()[0].strip()
        p.stdin.close()
        return result

    def get_screen_width(self):
        p = Popen(["xwininfo -root | egrep 'Width:'"],
                  shell=True, encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        return int(result.split(' ')[-1])

    def get_packages_status(self):
        p = Popen(["check-packages.sh"], shell=True, encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        return result

    def get_volume(self):
        p = Popen(["pamixer", "--get-volume"], encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        return result

    def get_cputemp(self):
        p = Popen(['cputemp.sh'], shell=True, encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        return result

    def qemu_status(self):
        p = Popen(['qemu-status win10'], shell=True, encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        if result == 'on':
            return True
        else:
            return False

    def synergy_status(self):
        p = Popen(['user-service-status synergys'], shell=True, encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        if result == 'on':
            return True
        else:
            return False

class bar_Output:
    def __init__(self, cfg=default_config):
        self.cfg = cfg
        self.margin = cfg.margin
        self.padding = cfg.padding
        self.colors = cfg.colors
    
    def write_icon(self, s):
        return ('%{T2}' + s + '%{T-}')

    def write_offset(self, offset):
        return ('%{O' + str(offset) + '}')

    def write_spaces(self, nspaces):
        if nspaces > 0:
            return ('%{T1}' + (' '*nspaces) + '%{T-}')
        else:
            return ''

    def write_simple_block(self, label, color, val_color, width, val):
        nspaces = width - len(val)
        return ('%{U' + self.colors[color] + '}' +
                '%{F' + self.colors[color] + '}' +
                '%{+u}' +
                self.write_offset(self.padding) +
                '' + label + ' ' + self.write_spaces(nspaces) +
                '%{F' + self.colors[val_color] + '}' + val +
                self.write_offset(self.padding) +
                '%{-u}' +
                self.write_offset(self.margin))

    def write_multi_block(self, color, sections):
        s = ''
        s += '%{U' + self.colors[color] + '}' + '%{+u}'
        s += self.write_offset(self.padding)
        for section in sections:
            [scolor, sval, swidth] = section
            s += '%{F' + self.colors[scolor] + '}'
            nspaces = swidth - len(sval)
            s += self.write_spaces(nspaces)
            s += sval
        s += self.write_offset(self.padding)
        s += '%{-u}'
        s += self.write_offset(self.margin)
        return s

class i3p_App:
    def load_state(self):
        self.state = json_from_file(i3path('state'))

    def write_state(self):
        json_to_file(self.state, i3path('state'))

    def __init__(self, cfg=default_config):
        self.cache = {
            'active_project': '',
            'i3_ws': {
                'result': '',
                'lemonbar': ''},
            'values': {
                'qemu': '',
                'synergy': '',
                'cpu': '',
                'mem': '',
                'diskio': '',
                'netspeed': '',
                'fsusage': '',
                'btcprice': '',
                'volume': '',
                'packages': '',
                'date': '',
                'time': '',
                'battery': '',
                'cputemp': ''
            },
            'blocks': {
                'qemu': '',
                'synergy': '',
                'cpu': '',
                'mem': '',
                'diskio': '',
                'netspeed': '',
                'fsusage': '',
                'btcprice': '',
                'volume': '',
                'packages': '',
                'date': '',
                'time': '',
                'battery': '',
                'cputemp': ''
            },
            'main': '',
            'output': '',
            'current': ''
        }
        self.cfg = cfg

    def init(self):
        self.util = i3p_Util()
        self.out = bar_Output()
        try:
            self.load_state()
        except:
            self.state = {
                'aliases': {
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
                }}

    def cache_or(self, ks, default=None):
        x = self.cache
        try:
            for k in ks:
                x = x[k]
            return x
        except:
            return default

    def cache_save(self, ks, val):
        x = self.cache
        for k in ks[:-1]:
            if k not in x.keys():
                x[k] = {}
            x = x[k]
        x[ks[-1]] = val

    def get_state(self, ks, default=None):
        x = self.state
        try:
            for k in ks:
                x = x[k]
            return x
        except:
            return default

    def set_state(self, ks, val, write=False):
        x = self.state
        for k in ks[:-1]:
            if k not in x.keys():
                x[k] = {}
            x = x[k]
        x[ks[-1]] = val
        if write:
            self.write_state()

    def del_state(self, ks, write=False):
        x = self.state
        try:
            for k in ks[:-1]:
                x = x[k]
            del x[ks[-1]]
            if write:
                self.write_state()
        except:
            pass
    
    def add_ws_alias(self, pname, wname, walias):
        if walias == None or walias == '':
            return self.remove_ws_alias(pname, wname)
        elif not (check_pname(pname) and check_wname(wname) and
                  is_str(walias)):
            print('add_ws_alias: invalid arguments (%s, %s, %s)' %
                  (pname, wname, walias))
        else:
            self.set_state(['aliases',pname,wname], walias, True)

    def remove_ws_alias(self, pname, wname):
        if not (check_pname(pname) and check_wname(wname)):
            print('remove_ws_alias: invalid arguments (%s, %s)' %
                  (pname, wname))
        else:
            self.del_state(['aliases',pname,wname], True)

    def get_ws_alias(self, wname, pname=None):
        if pname == None:
            pname = self.cache_or(['active_project'])
        return self.get_state(['aliases',pname,str(wname)])

    def label_workspace(self):
        self.update_all_ws()
        alias = self.util.rofi_select(
            [], 'Enter workspace label:')
        [pname,wname] = self.parse_ws_name(
            self.get_visible_ws()['name'])
        self.add_ws_alias(pname, wname, alias)

    def i3_msg(self, mtype, marg):
        p = Popen(['i3-msg -t %s %s' % (mtype, marg)],
                  shell=True, encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        return result

    def i3_get_workspaces(self):
        return self.i3_msg('get_workspaces', '')

    def i3_goto_workspace(self, pname, wname):
        return self.i3_msg('command', 'workspace %s_%s' % (pname,str(wname)))

    def write_main_output(self):
        s = ''
        blocks = ['qemu',
                  'synergy',
                  'cpu',
                  'cputemp',
                  'mem',
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
            s += self.cache_or(['blocks',name], '')
        return s

    def write_full_output(self):
        return ''.join(
            ['%{l}',
             self.cache_or(['i3_ws','lemonbar'], ''),
             '%{r}',
             self.cache_or(['main'], '')]
        )

    def update_main_output(self):
        self.cache_save(['main'], self.write_main_output())

    def update_output(self):
        self.cache_save(['output'], self.write_full_output())

    def update_output_all(self):
        self.update_main_output()
        self.update_output()

    def render_block(self, name, vals):
        o = self.out
        if name == 'qemu':
            status = vals
            if status == True:
                icon = ''
                color = 'green'
            else:
                icon = ''
                color = 'fg-dim'
            return o.write_multi_block(
                color,
                [[color, o.write_icon(icon), 0],
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
            return o.write_multi_block(
                color,
                [[color, o.write_icon(icon), 0],
                 ['fg', ' synergy', 0]]
            )
        elif name == 'cpu':
            cpu = vals
            return o.write_simple_block(
                o.write_icon(''),
                'green', 'fg', 4, '%s%%' % cpu)
        elif name == 'mem':
            [memused, memmax] = vals
            return o.write_multi_block(
                'yellow',
                [['yellow', o.write_icon(''), 0],
                 ['fg', memused, 6],
                 ['yellow', ' /', 0],
                 ['fg', memmax, 6]]
            )
        elif name == 'diskio':
            [diskread, diskwrite] = vals
            return o.write_multi_block(
                'cyan',
                [['cyan', o.write_icon(''), 0],
                 ['fg', diskread, 7],
                 ['cyan', ' ' + o.write_icon(''), 0],
                 ['fg', diskwrite, 7],
                 ['cyan', ' ' + o.write_icon(''), 0]]
            )
        elif name == 'netspeed':
            [netdown, netup] = vals
            return o.write_multi_block(
                'blue',
                [['blue', o.write_icon(''), 0],
                 ['fg', netdown, 7],
                 ['blue', ' ' + o.write_icon(''), 0],
                 ['fg', netup, 7],
                 ['blue', ' ' + o.write_icon(''), 0]]
            )
        elif name == 'fsusage':
            [fsused, fssize] = vals
            return o.write_multi_block(
                'purple',
                [['purple', o.write_icon(''), 0],
                 ['fg', ' ' + fsused, 0],
                 ['purple', ' /', 0],
                 ['fg', fssize, 0]]
            )
        elif name == 'btcprice':
            btcprice = vals
            return o.write_simple_block(
                o.write_icon(''),
                'green', 'fg', 4, btcprice)
        elif name == 'volume':
            volume = vals
            return o.write_simple_block(
                o.write_icon(''),
                'orange', 'fg', 4, volume+'%')
        elif name == 'packages':
            pstatus = vals
            return o.write_simple_block(
                o.write_icon(''), 'cyan', 'fg', 2, pstatus)
        elif name == 'date':
            datestr = vals
            return o.write_simple_block(
                o.write_icon(''), 'blue', 'fg', 10, datestr)
        elif name == 'time':
            timestr = vals
            return o.write_simple_block(
                o.write_icon(''), 'purple', 'fg', 8, timestr)
        elif name == 'battery':
            try:
                percent = int(vals)
                return o.write_simple_block(
                    o.write_icon(''), 'yellow', 'fg', 4, percent+'%'
                )
            except:
                return ''
        elif name == 'cputemp':
            temp = vals
            return o.write_simple_block(
                o.write_icon(''), 'orange', 'fg', 4, temp+'°'
            )
        else:
            return ''

    def update_block(self, name, vals, redraw=False):
        prev = self.cache_or(['values',name])
        if prev != vals:
            self.cache_save(['values',name], vals)
            self.cache_save(['blocks',name],
                            self.render_block(name, vals))
            if redraw:
                self.update_output_all()

    def update_from_conky(self, conkyline):
        try:
            j = json.loads(conkyline.strip())
        except:
            print('update_from_conky: unable to parse json')
            return False
        for k in j.keys():
            self.update_block(k, j[k])
        return True

    def get_active_project(self):
        return open(i3path('active')).readlines()[0].strip()

    def write_active_project(self, pname):
        f = open(i3path('active'),'w')
        print(pname, end='\n', file=f)
        f.close()

    def get_last_project(self):
        return open(i3path('prev')).readlines()[0].strip()

    def write_last_project(self, pname):
        f = open(i3path('prev'),'w')
        print(pname, end='\n', file=f)
        f.close()

    def get_project_list(self):
        return [s.strip() for s in
                open(i3path('projects')).readlines()]

    def write_project_list(self, pnames):
        f = open(i3path('projects'),'w')
        print('\n'.join(pnames), end='\n', file=f)
        f.close()

    def update_active_project(self):
        self.cache_save(['active_project'], self.get_active_project())

    def ws_order(self, ws):
        wname = '_'.join(ws['name'].split('_')[1:])
        if len(wname) == 0:
            print('ws_order: empty name, returning -1')
            return -1
        if wname[:2] == '10':
            return 10
        else:
            return int(wname[0])
    
    def write_project_block(self, name, active, wscount):
        o = self.out
        colors = self.cfg.colors
        padding = self.cfg.padding
        margin = self.cfg.margin
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
        s += o.write_offset(padding)
        if active:
            s += name
        else:
            s += name[:1]
        if not active:
            s += '[%d]' % wscount
        s += o.write_offset(padding)
        s += '%{B-}%{F-}'
        s += o.write_offset(margin)
        return s

    def parse_ws_name(self, raw_name):
        pname = raw_name.split('_')[0]
        wname = '_'.join(raw_name.split('_')[1:])
        return [pname, wname]

    def update_all_ws(self):
        self.cache_save(
            ['i3_ws','list'],
            json.loads(self.i3_get_workspaces()))

    def project_active_workspaces(self, all_ws=None):
        if all_ws == None:
            all_ws = self.cache_or(['i3_ws','list'], [])
        result = {}
        for ws in all_ws:
            [pname, wname] = self.parse_ws_name(ws['name'])
            if pname in result.keys():
                result[pname] += [wname]
            else:
                result[pname] = [wname]
        return result

    def write_projects_section(self, all_ws):
        pactive = self.cache_or(['active_project'])
        proj_aws = self.project_active_workspaces(all_ws)
        pnames = proj_aws.keys()

        s = ''
        s += '%{-u}'
        for pname in proj_aws.keys():
            if pname != pactive:
                s += self.write_project_block(pname, False, len(proj_aws[pname]))
        s += self.write_project_block(pactive, True, None)
        return s

    def set_latest_project_ws(self, pname, wname):
        self.set_state(
            ['project',pname,'latest_ws'], wname, True)

    def latest_project_ws(self, pname):
        return self.get_state(['project',pname,'latest_ws'], '1')

    def update_workspaces(self, all_ws_str):
        o = self.out
        update = False

        prev_state = self.state
        self.load_state()
        if self.state != prev_state:
            update = True

        prev_active = self.cache_or(['active_project'])
        self.update_active_project()
        if prev_active != self.cache_or(['active_project']):
            update = True

        if self.cache_or(['i3_ws','result']) != all_ws_str:
            update = True
            self.cache_save(['i3_ws','result'], all_ws_str)

        if update:
            s = ''
            try:
                all_ws = json.loads(all_ws_str)
            except:
                print('update_workspaces: unable to parse all_ws_str')
                return
            self.cache_save(['i3_ws','list'], all_ws)
            visible_ws = self.get_visible_ws()
            [vis_pname, vis_wname] = self.parse_ws_name(visible_ws['name'])
            self.set_latest_project_ws(vis_pname, vis_wname)
            pactive = self.cache_or(['active_project'])
            s += self.write_projects_section(all_ws)
            s += o.write_offset(o.margin)
            all_ws_sorted = sorted(all_ws, key=self.ws_order)
            for ws in all_ws_sorted:
                [pname,wname] = self.parse_ws_name(ws['name'])
                walias = self.get_ws_alias(wname)
                if walias == None:
                    wdisplay = wname
                else:
                    wdisplay = wname + '[' + walias + ']'
                wactive = (pname == pactive)
                if wactive:
                    color = {True: 'fg', False: 'fg-dim'}[ws['visible']]
                    s += o.write_multi_block(
                        color,
                        [[color, wdisplay, 0]]
                    )
            self.cache_save(['i3_ws','lemonbar'], s)
            self.update_output()

    def get_visible_ws(self):
        return [ws for ws in self.cache_or(['i3_ws','list'])
                if ws['visible']][0]
    
    def run(self, args=None):
        app = self

        class i3ws_Thread(Thread):
            def run(self):
                while True:
                    
                    app.update_workspaces( app.i3_get_workspaces() )
                    time.sleep(0.05)

        class conky_Thread(Thread):
            def run(self):
                self.ck = Popen(['conky -c ~/.i3/i3proj/conkyrc'],
                                shell=True, encoding='utf8', stdout=PIPE)
                while True:
                    result = str(self.ck.stdout.readline())
                    success = app.update_from_conky(result)
                    if not success:
                        break
                    app.update_output_all()

        class volume_Thread(Thread):
            def run(self):
                while True:
                    app.update_block('volume', app.util.get_volume(), True)
                    time.sleep(0.1)

        class output_Thread(Thread):
            def run(self):
                width = app.util.get_screen_width()
                self.lb = subprocess.Popen(
                    ['INFINALITY_FT="ultimate" lemonbar -g %dx45 -o 0 -u 2' % width +
                     ' -B' + app.cfg.colors['bg'] +
                     ' -f \'sauce code pro semibold:pixelsize=25\'' +
                     ' -f \'fontawesome:pixelsize=26\''],
                    shell=True, encoding='utf8', stdin=PIPE)
                while True:
                    if app.cache_or(['output']) != app.cache_or(['current']):
                        output = app.cache_or(['output'], '')
                        print(output, end='\n', file=self.lb.stdin)
                        self.lb.stdin.flush()
                        app.cache_save(['current'], output)
                    time.sleep(0.05)

        class misc_Thread(Thread):
            def run(self):
                while True:
                    app.update_block(
                        'qemu', app.util.qemu_status(), True)
                    app.update_block(
                        'synergy', app.util.synergy_status(), True)
                    app.update_block(
                        'cputemp', app.util.get_cputemp(), True)
                    time.sleep(0.5)

        class packages_Thread(Thread):
            def run(self):
                while True:
                    app.update_block(
                        'packages', app.util.get_packages_status(), True)
                    time.sleep(120)

        app.update_active_project()
        pname = app.cache_or(['active_project'])
        if pname != None:
            app.i3_goto_workspace(
                pname, app.latest_project_ws(pname))

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

    def transfer_project(self, pname=None):
        plist = self.get_project_list()
        if pname == None:
            pname = self.util.rofi_select(
                plist, 'Transfer window to project:')
        if pname not in plist:
            print('invalid project name: %s' % pname)
        else:
            self.update_all_ws()
            active_ws = self.get_visible_ws()
            if pname != None and active_ws != None:
                wname = pname + '_' + str(self.ws_order(active_ws))
                self.i3_msg('command',
                            'move container to workspace ' + wname)

    def switch_project(self, pname):
        plist = self.get_project_list()
        if pname in plist:
            self.write_last_project(self.get_active_project())
            self.write_active_project(pname)
            wname = self.latest_project_ws(pname)
            self.i3_goto_workspace(pname, wname)
            return True
        else:
            print('switch_project: invalid project name: %s' % pname)
            return False

    def run_switch_project(self):
        plist = self.get_project_list()
        pname = self.util.rofi_select(plist, 'Switch to project:')
        self.switch_project(pname)

    def create_project(self, args=None):
        plist = self.get_project_list()
        pname = self.util.rofi_select(
            [], 'Enter name for new project:')
        if pname == None or len(pname.strip()) == 0:
            print('create_project: no project name')
            return
        if pname not in plist:
            plist += [pname]
            self.write_project_list(plist)
        self.switch_project(pname)

    def delete_project(self, pdelete=None):
        self.update_all_ws()
        proj_aws = self.project_active_workspaces()
        plist = self.get_project_list()
        plist_empty = [pname for pname in plist
                       if pname not in proj_aws.keys()]
        if pdelete == None:
            pdelete = self.util.rofi_select(
                plist_empty, 'Delete project:')
        if pdelete not in plist_empty:
            print('\'%s\' is not a valid empty project' % pname)
        else:
            new_plist = [pname for pname in plist if pname != pdelete]
            if len(new_plist) == 0:
                print('unable to delete, project list would be empty')
            else:
                self.write_project_list(new_plist)

    def next_project(self):
        plist = self.get_project_list()
        pactive = self.get_active_project()
        if pactive not in plist:
            print('next_project: active project not found in list')
        else:
            idx = plist.index(pactive)
            if idx == len(plist)-1:
                next_idx = 0
            else:
                next_idx = idx+1
            self.switch_project(plist[next_idx])

    def prev_project(self):
        plist = self.get_project_list()
        pactive = self.get_active_project()
        if pactive not in plist:
            print('prev_project: active project not found in list')
        else:
            idx = plist.index(pactive)
            if idx == 0:
                prev_idx = len(plist)-1
            else:
                prev_idx = idx-1
            self.switch_project(plist[prev_idx])

    def recent_project(self):
        plist = self.get_project_list()
        pactive = self.get_active_project()
        plast = self.get_last_project()
        if plast == pactive:
            print('recent_project: \'%s\' already active' % plast)
        elif plast not in plist:
            print('recent_project: \'%s\' not in project list' % plast)
        else:
            self.switch_project(plast)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Workspace group manager for i3wm')
    parser.add_argument('action', nargs=1, choices=[
        'run',
        'active-project','transfer-project',
        'create-project','delete-project','set-ws-label',
        'switch-project','recent-project','next-project','prev-project'
        ])
    args=parser.parse_args()
    action = args.action[0]
    app = i3p_App()
    app.init()
    if action == 'run':
        app.run()
    elif action == 'transfer-project':
        app.transfer_project()
    elif action == 'switch-project':
        app.run_switch_project()
    elif action == 'next-project':
        app.next_project()
    elif action == 'prev-project':
        app.prev_project()
    elif action == 'recent-project':
        app.recent_project()
    elif action == 'create-project':
        app.create_project(args)
    elif action == 'delete-project':
        app.delete_project()
    elif action == 'set-ws-label':
        app.label_workspace()
    elif action == 'active-project':
        print(app.get_active_project())
    elif action == 'next-project':
        app.next_project()
    else:
        print('invalid command-line arguments')
