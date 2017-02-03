#!/usr/bin/python3

import sys, time
import subprocess
from subprocess import Popen, PIPE, run
from itertools import takewhile


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

colors = {'fg': '#c8c8c8',
          'green': '#b5bd68',
          'purple': '#b294bb',
          'blue': '#81a2be',
          'cyan': '#8abeb7',
          'orange': '#de935f'
}

bmargin = 6
bpadding = 5

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

def write_cpu_block(cpu):
    return write_simple_block(
        write_icon(''),
        'green', 'fg', 4, '%s%%' % cpu)

def write_diskio_block(diskread, diskwrite):
    return write_multi_block(
        'cyan',
        [['cyan', write_icon(''), 0],
         ['fg', diskread, 7],
         ['cyan', ' ' + write_icon(''), 0],
         ['fg', diskwrite, 7],
         ['cyan', ' ' + write_icon(''), 0]]
    )

def write_netspeed_block(netdown, netup):
    return write_multi_block(
        'blue',
        [['blue', write_icon(''), 0],
         ['fg', netdown, 7],
         ['blue', ' ' + write_icon(''), 0],
         ['fg', netup, 7],
         ['blue', ' ' + write_icon(''), 0]]
    )

def write_fsusage_block(fsused, fssize):
    return write_multi_block(
        'purple',
        [['purple', write_icon(''), 0],
         ['fg', ' ' + fsused, 0],
         ['purple', ' /', 0],
         ['fg', fssize, 0]]
    )

def write_btcprice_block(btcprice):
    return write_simple_block(
        write_icon(''),
        'green', 'fg', 4, btcprice)

def write_audio_volume(volume):
    return write_simple_block(
        write_icon(''),
        'orange', 'fg', 4, volume+'%')

def write_package_status(pstatus):
    return write_simple_block(
        write_icon(''), 'cyan', 'fg', 0, pstatus)

def write_date_block(datestr):
    return write_simple_block(
        write_icon(''), 'blue', 'fg', 10, datestr)

def write_time_block(timestr):
    return write_simple_block(
        write_icon(''), 'purple', 'fg', 8, timestr)

def write_lemonbar_output(conkyline):
    [cpu, memused, memmax, diskread, diskwrite, netdown, netup,
     fsused, fssize, datestr, timestr, btcprice, pstatus,
     volume] = (
        conkyline.strip().split(';')
    )
    return ''.join(
        ['%{r}',
         write_cpu_block(cpu),
         write_diskio_block(diskread, diskwrite),
         write_netspeed_block(netdown+'K', netup+'K'),
         write_fsusage_block(fsused, fssize),
         write_btcprice_block(btcprice),
         write_audio_volume(volume),
         write_package_status(pstatus),
         write_date_block(datestr),
         write_time_block(timestr)
        ])

ck = Popen(['conky -c ~/.i3/conky/conkyrc_raw'], shell=True, encoding='utf8', stdout=PIPE)
# lb = subprocess.Popen(["lemonbar -g 3840x55 -o -2 -u 2 -B\#282828 -f 'Lato Semibold:pixelsize=24' -f 'FontAwesome:pixelsize=27' -f 'Source Code Pro Medium:pixelsize=26'"], shell=True, encoding='utf8', stdin=PIPE)
# lb = subprocess.Popen(["lemonbar -g 3840x55 -o -2 -u 2 -B\#282828 -f 'Sauce Code Pro Semibold:pixelsize=26' -f 'FontAwesome:pixelsize=27'"], shell=True, encoding='utf8', stdin=PIPE)
# lb = subprocess.Popen(["lemonbar -g 3840x55 -o 0 -u 2 -B\#282828 -f 'Inconsolata Bold:pixelsize=30' -f 'FontAwesome:pixelsize=27'"], shell=True, encoding='utf8', stdin=PIPE)
lb = subprocess.Popen(["lemonbar -g 3840x55 -o 0 -u 2 -B\#282828 -f 'sauce code pro medium:size=12' -f 'fontawesome:size=13'"], shell=True, encoding='utf8', stdin=PIPE)

while True:
    s = str(ck.stdout.readline())
    # print( write_lemonbar_output(s) )
    print('%s' % write_lemonbar_output(s), end='\n', file=lb.stdin)
    lb.stdin.flush()
    # print("%s ; %s ; %s" % (cpu, qemu_status(), synergy_status()))
