# This file is placed in the Public Domain.


"todo list"


import time


from ..disk    import write
from ..object  import Object, update
from ..persist import find, fntime, getpath
from .         import elapsed


class Todo(Object):

    def __init__(self):
        Object.__init__(self)
        self.txt = ''


def dne(event):
    if not event.args:
        event.reply("dne <txt>")
        return
    selector = {'txt': event.args[0]}
    nmr = 0
    for fnm, obj in find('todo', selector):
        nmr += 1
        obj.__deleted__ = True
        write(obj, getpath(obj))
        event.done()
        break
    if not nmr:
        event.reply("nothing todo")


def tdo(event):
    if not event.rest:
        nmr = 0
        for fnm, obj in find('todo'):
            tdo = Todo()
            update(tdo, obj)
            lap = elapsed(time.time()-fntime(fnm))
            event.reply(f'{nmr} {tdo.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply("no todo")
        return
    obj = Todo()
    obj.txt = event.rest
    write(obj, getpath(obj))
    event.done()
