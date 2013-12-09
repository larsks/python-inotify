'''
    Low level inotify wrapper
    originally from:
    http://code.activestate.com/recipes/576375-low-level-inotify-wrapper/
'''

import os
import struct
import errno
from collections import namedtuple
from ctypes import cdll, c_int, POINTER
from errno import errorcode

from flags import *

read_buf_size    = 1024
inotify_evt_size = struct.calcsize('iIII')

inotify_event = namedtuple('inotify_event', ['path', 'mask', 'cookie', 'name'])

libc = cdll.LoadLibrary('libc.so.6')
libc.__errno_location.restype = POINTER(c_int)
def geterr(): return libc.__errno_location().contents.value

FLAG_NAMES = dict(
        (k,v) for k,v in locals().items() if k.startswith('IN_'))
FLAG_VALS = dict(
        (v,k) for k,v in locals().items() if k.startswith('IN_'))

class InotifyError (OSError):
    pass

class Inotify(object):
    '''A low-level inotify class for use in poll/select based event
    loops.'''

    def __init__(self):
        self.wd = {}
        self.fd = libc.inotify_init()

        if self.fd == -1:
            raise OSError(geterr(), 'Failed to initialize inotify object')


    def read(self):
        '''Read a notification record from the inotify
        file descriptor.'''

        buf = os.read(self.fd, read_buf_size)
        wd, mask, cookie, name_len = struct.unpack(
                'iIII',
                buf[0:inotify_evt_size])
        name = struct.unpack(
                '%ds' % name_len,
                buf[inotify_evt_size:inotify_evt_size+name_len])
        name = name[0].rstrip('\x00')

        path = [k for k,v in self.wd.items() if v == wd][0]
        return inotify_event(path, mask, cookie, name)


    def add_watch(self, path, mask):
        '''Add a watch on the given path with the given mask.'''

        if path in self.wd:
            raise OSError(errno.EEXIST,
                    'A watch on %s already exists' % path)

        wd = libc.inotify_add_watch(self.fd, path, mask)
        if wd == -1:
            raise OSError(geterr(), 'Failed to add watch')

        self.wd[path] = wd


    def rm_watch(self, path):
        if not path in self.wd:
            raise OSError(errno.ENOENT, 'No watch exists on %s' % path)

        wd = self.wd[path]
        ret = libc.inotify_rm_watch(self.fd, wd)
        if ret == -1:
            raise OSError(geterr(), 'Failed to remove watch')
        
        del self.wd[path]


    def close(self):
        ret = os.close(self.fd)
        if ret == -1:
            raise OSError(geterr(), 'Failed to close inotify descriptor')


    def fileno(self):
        '''Returns the integer file descriptor of this inotify object.'''
        return self.fd

def mask_str(mask):
    return ' | '.join(name for name, val in FLAG_NAMES.items()
            if name != 'IN_ALL_EVENTS' and val & mask)

