# Low-level inotify interface

This is a Python interface to the Linux [inotify][] subsystem.

## Example

Put this script in a file and run it:

    import inotify
    from inotify.flags import *
    import select

    ifd = inotify.Inotify()
    ifd.add_watch('/tmp', IN_ALL_EVENTS)

    poll = select.poll()
    poll.register(ifd)

    while True:
        events = dict(poll.poll())

        if ifd.fileno() in events:
            res = ifd.read()
            print res

While the script is running, manipulate files in `/tmp`.

[inotify]: http://en.wikipedia.org/wiki/Inotify

