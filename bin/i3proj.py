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
    def __init__(self,margin,padding,colors,icons,item_colors):
        self.margin = margin
        self.padding = padding
        self.colors = colors
        self.icons = icons
        self.item_colors = item_colors

color_themes = {
    'gruvbox': {
        'fg': '#fdf4c1',
        #'bg': '#282828',
        'bg': '#32302f',
        'fg-dim': '#988974',
        # 'value': '#d5c4a1',
        'value': '#fdf4c1',
        'bg-light': '#ebdbb2',
        'fg-dark': '#121314',
        'green': '#b8bb26',
        'purple': '#b16286',
        'blue': '#83a598',
        'cyan': '#8ec07c',
        'orange': '#d79921',
        'yellow': '#fabd2f'
    },
    'base16-default-dark': {
        'fg': '#e8e8e8',
        'bg': '#181818',
        'fg-dim': '#a8a8a8',
        'value': '#d8d8d8',
        'bg-light': '#d8d8d8',
        'fg-dark': '#121212',
        'green': '#a1b56c',
        'purple': '#ba8baf',
        'blue': '#7cafc2',
        'cyan': '#86c1b9',
        'orange': '#dc9656',
        'yellow': '#f7ca88'
    }
}

default_config = i3p_Config(
    margin=8,
    padding=4,
    colors = color_themes['gruvbox'],
    icons = {'code': '',
             'server': 'S',
             'client': 'C',
             'web': '',
             'work': '',
             'chrome': '',
             'firefox': '',
             'shell': '',
             # 'shell': '',
             'media': '',
             'video': '',
             'music': '',
             'tv': '',
             'settings': '',
             'user': ''
    },
    item_colors = {'ws_icon': 'blue',
                   'ws_label': 'blue'}
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
        input = '\n'.join(options)
        if len(options) > 0:
            cmd = ['rofi', '-dmenu', '-sync', '-p', '', '-mesg', message,
                   '-l', str(min(10,len(options))), '-no-custom']
        else:
            cmd = ['rofi', '-dmenu', '-sync', '-p', '> ', '-mesg', message,
                   '-l', '1']
        p = Popen(cmd, encoding='utf8', stdin=PIPE, stdout=PIPE)
        if len(options) > 0:
            print(input, end='\n', file=p.stdin, flush=True)
        result = p.communicate()[0].strip()
        p.stdin.close()
        return result

    def get_window_title(self):
        p = Popen(["window-title.sh"],
                  shell=True, encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
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

    def get_cpufreq(self):
        try:
            lines = open(i3path('cpufreq')).readlines()[1:]
            maxfreq = 0
            for line in lines:
                val = int(float(line.strip()))
                if val > maxfreq:
                    maxfreq = val
            if maxfreq == 0:
                return None
            else:
                return maxfreq
        except:
            return None

    def systemd_status(self, name):
        p = Popen(['service-status', name], encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        if result == 'on':
            return True
        else:
            return False

    def service_exists(self, name):
        p = Popen(['service-exists', name], encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        if result == 'yes':
            return True
        else:
            return False

    def user_service_exists(self, name):
        p = Popen(['user-service-exists', name], encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        if result == 'yes':
            return True
        else:
            return False

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

    def lookup_color(self, color):
        if color in self.colors.keys():
            return self.colors[color]
        else:
            return self.colors['fg']
    
    def write_icon(self, s):
        return ('%{T-}' + s + '%{T-}')

    def write_with_font(self, s, fontidx):
        return ('%{T' + str(fontidx) + '}' + s + '%{T-}')

    def write_with_fg(self, s, color, current=None):
        if current == None:
            current_out = '-'
        else:
            current_out = self.lookup_color(current)
        return ('%{F' + self.lookup_color(color) + '}' + s + '%{F' + current_out + '}')

    def write_with_bg(self, s, color, current=None):
        if current == None:
            current_out = '-'
        else:
            current_out = self.lookup_color(current)
        return ('%{B' + self.lookup_color(color) + '}' + s + '%{B' + current_out + '}')

    def write_offset(self, offset):
        return ('%{O' + str(offset) + '}')

    def write_spaces(self, nspaces):
        if nspaces > 0:
            return ('%{T1}' + (' '*nspaces) + '%{T-}')
        else:
            return ''

    def write_simple_block(self, label, color, val_color, width, val):
        nspaces = width - len(val)

        return ('%{U' + self.lookup_color(color) + '}' +
                '%{F' + self.lookup_color(color) + '}' +
                '%{+u}' +
                self.write_offset(self.padding) +
                '' + label + ' ' + self.write_spaces(nspaces) +
                '%{F' + self.lookup_color(val_color) + '}' + val +
                self.write_offset(self.padding) +
                '%{-u}' +
                self.write_offset(self.margin))

    def write_multi_block(self, color, sections):
        s = ''
        s += '%{U' + self.lookup_color(color) + '}' + '%{+u}'
        s += self.write_offset(self.padding)
        for section in sections:
            [scolor, sval, swidth] = section
            s += '%{F' + self.lookup_color(scolor) + '}'
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
                'cputemp': '',
                'cpufreq': ''
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
                'cputemp': '',
                'cpufreq': ''
            },
            'main': '',
            'output': '',
            'current': ''
        }
        self.cfg = cfg
        self.lb = None
        self.lb2 = None

    def init(self):
        self.util = i3p_Util()
        self.out = bar_Output()
        try:
            self.load_state()
        except:
            self.state = {
                'labels': {}
            }

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
    
    def add_ws_label(self, pname, wname, wlabel):
        if wlabel == None or wlabel == '':
            return self.remove_ws_label(pname, wname)
        elif not (check_pname(pname) and check_wname(wname) and
                  type(wlabel)==str):
            print('add_ws_label: invalid arguments (%s, %s, %s)' %
                  (pname, wname, wlabel))
        else:
            self.set_state(['labels',pname,wname], wlabel, True)

    def remove_ws_label(self, pname, wname):
        if not (check_pname(pname) and check_wname(wname)):
            print('remove_ws_label: invalid arguments (%s, %s)' %
                  (pname, wname))
        else:
            self.del_state(['labels',pname,wname], True)

    def get_ws_label(self, wname, pname=None):
        if pname == None:
            pname = self.cache_or(['active_project'])
        return self.get_state(['labels',pname,str(wname)])

    def label_workspace(self):
        self.update_all_ws()
        response = self.util.rofi_select(
            [], 'Enter workspace label').strip()
        [pname,wname] = self.parse_ws_name(
            self.get_visible_ws()['name'])
        self.add_ws_label(pname, wname, response)

    def i3_msg(self, mtype, marg):
        p = Popen(['i3-msg -t %s %s' % (mtype, marg)],
                  shell=True, encoding='utf8', stdout=PIPE)
        result = p.communicate()[0].strip()
        return result

    def i3_get_workspaces(self):
        return self.i3_msg('get_workspaces', '')

    def i3_goto_workspace(self, pname, wname):
        return self.i3_msg('command', 'workspace %s_%s' % (pname,str(wname)))

    def update_window_title(self):
        title = self.util.get_window_title()
        if title != self.cache_or(['window_title'],''):
            self.cache_save(['window_title'],title)
            self.update_output()
            self.update_display()

    def write_main_output(self):
        s = ''
        # blocks = ['volume',
        #          'battery',
        #          'date',
        #          'time']
        blocks = ['qemu',
                  'synergy',
                  'cpu',
                  'cputemp',
                  'mem',
                  'diskio',
                  'netspeed',
                  'fsusage',
                  'btcprice',
                  'packages',
                  'battery',
                  'volume',
                  'date',
                  'time']
        for name in blocks:
            s += self.cache_or(['blocks',name], '')
        return s

    def write_secondary_output(self):
        s = ''
        s += '%{c}'
        blocks = ['qemu',
                  'synergy',
                  'cpu',
                  # 'cpufreq',
                  'cputemp',
                  'mem',
                  'diskio',
                  'netspeed',
                  'fsusage',
                  'btcprice',
                  'packages']
        for name in blocks:
            s += self.cache_or(['blocks',name], '')
        return s

    def write_full_output(self):
        return ''.join(
            ['%{l}',
             self.cache_or(['i3_ws','lemonbar'], ''),
             '%{c}',
             self.cache_or(['window_title'], ''),
             '%{r}',
             self.cache_or(['main'], '')]
        )

    def update_main_output(self):
        self.cache_save(['main'], self.write_main_output())

    def update_secondary_output(self):
        self.cache_save(['secondary'], self.write_secondary_output())

    def update_output(self):
        self.cache_save(['output'], self.write_full_output())

    def update_output_all(self):
        self.update_main_output()
        self.update_output()
        # self.update_secondary_output()

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
                 ['value', ' qemu', 0]]
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
                 ['value', ' synergy', 0]]
            )
        elif name == 'cpu':
            cpu = vals
            cpufreq = self.cache_or(['cpufreq'])
            if cpufreq is None:
                return o.write_simple_block(
                    o.write_icon(''),
                    'green', 'value', 4, '%s%%' % cpu)
            else:
                return o.write_multi_block(
                    'green',
                    [['green', o.write_icon(''), 0],
                     ['value', '%s%%' % cpu, 5],
                     ['green', ' | ', 0],
                     ['value', '%s MHz' % cpufreq, 8]]
                )
        elif name == 'mem':
            [memused, memmax] = vals
            return o.write_multi_block(
                'yellow',
                [['yellow', o.write_icon(''), 0],
                 ['value', '  ' + memused, 0],
                 ['yellow', ' / ', 0],
                 ['value', memmax, 0]]
            )
        elif name == 'diskio':
            [diskread, diskwrite] = vals
            return o.write_multi_block(
                'cyan',
                [['cyan', o.write_icon(''), 0],
                 ['value', diskread, 8],
                 ['cyan', ' ' + o.write_icon(''), 0],
                 ['value', diskwrite, 8],
                 ['cyan', ' ' + o.write_icon(''), 0]]
            )
        elif name == 'netspeed':
            [netdown, netup] = vals
            return o.write_multi_block(
                'blue',
                [['blue', o.write_icon(''), 0],
                 ['value', netdown, 10],
                 ['blue', ' ' + o.write_icon(''), 0],
                 ['value', netup, 10],
                 ['blue', ' ' + o.write_icon(''), 0]]
            )
        elif name == 'fsusage':
            [fsused, fssize] = vals
            return o.write_multi_block(
                'purple',
                [['purple', o.write_icon(''), 0],
                 ['value', '  ' + fsused, 0],
                 ['purple', ' / ', 0],
                 ['value', fssize, 0]]
            )
        elif name == 'btcprice':
            btcprice = vals
            return o.write_simple_block(
                o.write_icon(''),
                'green', 'value', 4, btcprice)
        elif name == 'volume':
            volume = vals
            return o.write_simple_block(
                o.write_icon(''),
                'orange', 'value', 4, volume+'%')
        elif name == 'packages':
            pstatus = vals
            return o.write_simple_block(
                o.write_icon(''), 'cyan', 'value', 3, pstatus)
        elif name == 'date':
            datestr = vals
            return o.write_simple_block(
                o.write_icon(''), 'blue', 'value', 11, datestr)
        elif name == 'time':
            timestr = vals
            return o.write_simple_block(
                o.write_icon(''), 'purple', 'value', 8, timestr)
        elif name == 'battery':
            try:
                percent = int(vals)
                return o.write_simple_block(
                    o.write_icon(''), 'yellow', 'value', 4, str(percent)+'%'
                )
            except:
                return ''
        elif name == 'cputemp':
            temp = vals
            return o.write_simple_block(
                o.write_icon(''), 'orange', 'value', 4, temp+'°'
            )
        elif name == 'cpufreq':
            mhz = vals
            # o.write_icon('')
            return o.write_simple_block(
                o.write_icon(''),
                'green', 'value', 9, '%s MHz' % mhz
            )
        else:
            return ''

    def update_block(self, name, vals, redraw=True):
        prev = self.cache_or(['values',name])
        if prev != vals:
            self.cache_save(['values',name], vals)
            self.cache_save(['blocks',name],
                            self.render_block(name, vals))
            if redraw:
                self.update_output_all()
                self.update_display()

    def update_cpufreq(self):
        cpufreq = app.util.get_cpufreq()
        if cpufreq != None:
            self.cache_save(['cpufreq'], cpufreq)

    def update_from_conky(self, conkyline):
        try:
            j = json.loads(conkyline.strip())
        except:
            print('update_from_conky: unable to parse json')
            return False
        for k in j.keys():
            self.update_block(k, j[k], False)
        self.update_display()
        return True

    def get_active_project(self):
        try:
            return open(i3path('active')).readlines()[0].strip()
        except:
            return 'home'

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
        try:
            return [s.strip() for s in
                    open(i3path('projects')).readlines()]
        except:
            return ['home']

    def get_active_project_list(self):
        proj_aws = self.project_active_workspaces()
        return [pname for pname in self.get_project_list()
                if (pname in proj_aws.keys() and len(proj_aws[pname]) > 0)]

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
        s += name
        # if active:
        #     s += name
        # else:
        #     s += name[:1]
        # if not active:
        #     s += '<%d>' % wscount
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

        s = ''
        s += '%{-u}'
        for pname in self.get_project_list():
            if pname in proj_aws.keys():
                active = (pname == pactive)
                s += self.write_project_block(pname, active, len(proj_aws[pname]))
        return s

    def set_latest_project_ws(self, pname, wname):
        self.set_state(
            ['project',pname,'latest_ws'], wname, True)

    def latest_project_ws(self, pname):
        return self.get_state(['project',pname,'latest_ws'], '1')

    def update_display(self):
        if (app.lb != None and
            (app.cache_or(['output']) != app.cache_or(['current']))):
            output = app.cache_or(['output'], '')
            app.cache_save(['current'], output)
            print(output, end='\n', file=app.lb.stdin)
            app.lb.stdin.flush()
        if (app.lb2 != None and
            (app.cache_or(['secondary']) != app.cache_or(['current_secondary']))):
            output = app.cache_or(['secondary'], '')
            app.cache_save(['current_secondary'], output)
            print(output, end='\n', file=app.lb2.stdin)
            app.lb2.stdin.flush()

    def update_workspaces(self, all_ws_str):
        o = self.out
        update = False

        prev_state = self.state
        try:
            self.load_state()
            if self.state != prev_state:
                update = True
        except:
            pass

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
                wactive = (pname == pactive)
                if wactive:
                    color = {True: 'fg', False: 'fg-dim'}[ws['visible']]
                    wlabel = self.get_ws_label(wname)
                    if wlabel is None or len(wlabel) == 0:
                        label = None
                        icon = None
                    elif wlabel in self.cfg.icons.keys():
                        label = None
                        icon = self.cfg.icons[wlabel]
                    else:
                        label = wlabel
                        icon = None

                    wdisplay = wname
                    if icon != None:
                        icon_color = self.cfg.item_colors['ws_icon']
                        icon_padding = 8
                        label_out = o.write_with_fg(icon, icon_color, color)
                        label_out = (o.write_offset(icon_padding)
                                     + label_out
                                     + o.write_offset(4)
                        )
                        wdisplay += label_out
                    elif label != None:
                        label_color = self.cfg.item_colors['ws_label']
                        label_padding = 10
                        label_out = (o.write_offset(label_padding)
                                     + o.write_with_fg(label, label_color, color)
                                     # + o.write_offset(4)
                        )
                        wdisplay += label_out

                    b = o.write_multi_block(
                        color,
                        [[color, wdisplay, 0]]
                    )
                    s += b
                
            self.cache_save(['i3_ws','lemonbar'], s)
            self.update_output()
            self.update_display()

    def get_visible_ws(self):
        return [ws for ws in self.cache_or(['i3_ws','list'])
                if ws['visible']][0]
    
    def run(self, args=None):
        app = self

        if self.util.service_exists('libvirtd'):
            self.libvirtd_active = self.util.systemd_status('libvirtd')
        else:
            self.libvirtd_active = False

        class i3ws_Thread(Thread):
            def run(self):
                while True:
                    app.update_workspaces( app.i3_get_workspaces() )
                    time.sleep(0.15)

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
                    app.update_block('volume', app.util.get_volume())
                    time.sleep(0.2)

        class output_Thread(Thread):
            def run(self):
                width = app.util.get_screen_width()
                height = 46
                fsize = 'size=12'
                isize = 'size=11'
                app.lb = subprocess.Popen(
                    ['lemonbar -g %dx%d -o -1 -u 4' %
                     (width, height) +
                     ' -B' + app.cfg.colors['bg'] +
                     # ' -f \'source code pro medium:%s\'' % str(fsize) +
                     # ' -f \'sauce code pro semibold:%s\'' % str(fsize) +
                     ' -f \'inconsolata:%s\'' % str(fsize) +
                     ' -f \'fontawesome 5 pro regular:%s\'' % str(isize) +
                     ' -f \'fontawesome 5 brands:%s\'' % str(isize)],
                    shell=True, encoding='utf8', stdin=PIPE)
                # app.lb2 = subprocess.Popen(
                #     ['lemonbar -b -g %dx%d -o 0 -u 4' %
                #      (width, height) +
                #      ' -B' + app.cfg.colors['bg'] +
                #      ' -f \'source code pro medium:%s\'' % str(fsize) +
                #      ' -f \'fontawesome:%s\'' % str(isize)],
                #     shell=True, encoding='utf8', stdin=PIPE)
                app.update_display()
                while True:
                    time.sleep(1.0)

        class misc_Thread(Thread):
            def run(self):
                while True:
                    if app.libvirtd_active:
                        app.update_block('qemu', app.util.qemu_status())
                        app.update_block('synergy', app.util.synergy_status())
                    app.update_block('cputemp', app.util.get_cputemp())
                    time.sleep(0.5)

        class title_Thread(Thread):
            def run(self):
                while True:
                    app.update_window_title()
                    time.sleep(0.1)

        class i7z_Thread(Thread):
            def run(self):
                self.i7z = subprocess.Popen(
                    ['sudo i7z --logfile ~/.i3/i3proj/cpufreq --write l --nogui'],
                     shell=True, encoding='utf8', stdout=PIPE)
                while True:
                    app.update_cpufreq()
                    time.sleep(0.5)

        class packages_Thread(Thread):
            def run(self):
                while True:
                    packages = app.util.get_packages_status()
                    app.update_block('packages', packages)
                    time.sleep(60)

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

        # packages = packages_Thread()
        # packages.start()

        misc = misc_Thread()
        misc.start()

        # title = title_Thread()
        # title.start()

        output = output_Thread()
        output.start()

        i7z = i7z_Thread()
        i7z.start()

        output.join()    

    def transfer_project(self):
        plist = self.get_project_list()

        pws_list = []
        for wsidx in range(1,11):
            for pname in plist:
                pws_list += [pname + '_' + str(wsidx)]

        wname = self.util.rofi_select(
            pws_list, 'Transfer window to project:')

        if not (wname in pws_list):
            print('invalid workspace name: %s' % wname)
        else:
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
            [], 'Enter name for new project')
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
        self.update_workspaces( self.i3_get_workspaces() )
        plist = self.get_active_project_list()
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
        self.update_workspaces( self.i3_get_workspaces() )
        plist = self.get_active_project_list()
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
