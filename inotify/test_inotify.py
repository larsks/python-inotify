#!/usr/bin/python

import tempfile
import select
import errno

import inotify
from flags import *

def test_create_inotify():
    '''Verify that we can create an Inotify object'''
    i = inotify.Inotify()
    assert(i is not None)

def test_add_watch():
    '''Verify that we can call Inotify.add_watch without error'''
 
    i = inotify.Inotify()
    assert(i is not None)
    with tempfile.NamedTemporaryFile() as tmp:
        i.add_watch(tmp.name, IN_MODIFY)

def test_add_watch_fail():
    '''Verify that Inotify.add_watch raises an exception when called with
    an invalid path'''
    i = inotify.Inotify()
    assert(i is not None)

    try:
        i.add_watch('path-that-does-not-exist', 0)
    except OSError as detail:
        if detail.errno != errno.EINVAL:
            print 'ERRNO:', detail.errno, errno.EINVAL
            raise

def test_rm_watch():
    '''Verify that we can call Inotify.rm_watch without error'''
    i = inotify.Inotify()
    assert(i is not None)
    with tempfile.NamedTemporaryFile() as tmp:
        i.add_watch(tmp.name, IN_MODIFY)
        i.rm_watch(tmp.name)

def test_rm_watch_fail():
    '''Verify that Inotify.rm_watch raises an exception if called
    with an invalid path'''

    i = inotify.Inotify()
    assert(i is not None)
    try:
        i.rm_watch('path-that-does-not-exist')
    except OSError as detail:
        if detail.errno != errno.ENOENT:
            raise

def test_events():
    '''Verify that we receive an IN_MODIFY event when a file is modified'''

    i = inotify.Inotify()
    assert(i is not None)
    with tempfile.NamedTemporaryFile() as tmp:
        i.add_watch(tmp.name, IN_MODIFY)
        poll = select.poll()
        poll.register(i)
        state = 0
        received = []

        while True:
            events = dict(poll.poll(500))

            if i.fileno() in events:
                res = i.read()
                received.append(res.mask)

            if state == 0:
                tmp.write('This is a test.')
                tmp.flush()
                state = 1
            elif state == 1:
                break

    assert(IN_MODIFY in received)

def test_close():
    '''Verify that we can close an Inotify object with error'''
    i = inotify.Inotify()
    i.close()

def test_close_fail():
    '''Verify that Inotify.close() raises an exception if already closed'''
    i = inotify.Inotify()
    i.close()
    try:
        i.close()
    except OSError as detail:
        if detail.errno != errno.EBADF:
            raise

if __name__ == '__main__':
    test_events()

