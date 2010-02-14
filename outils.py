# -*- coding: utf-8 -*-

r"""
Miscellaneous tools for easing script output.

This module contains the following classes:

- `osplitter`, an output stream splitter
- `writecounter`, counts the number of write calls

The output stream splitter (`osplitter`)
========================================

When generating data from a typical simulation script, one usually
wants the output redirected into several places. A common use case is
to print log messages both to `stderr` and a file. The `osplitter`
class can be used as a drop-in replacement for streams like the
sys.stderr, with output redirected to several places by registering
different steam objects with the `osplitter`. In the following
example, log messages are output both to a temporary file and to
sys.stderr:

    >>> import sys, tempfile
    >>> import outils
    >>> outfile = tempfile.TemporaryFile()
    >>> ostream = outils.osplitter(outfile, sys.stdout)
    >>> print >>ostream, 'Logged message'
    Logged message
    >>> outfile.seek(0)
    >>> outfile.read()
    'Logged message\n'
    >>>

The write counter (`writecounter`)
==================================

This class implements a writer which simply counts the number of write
operations. This can for example be used in conjunction for polling
the progress of the data processing from a separate thread.

"""

__all__=['osplitter', 'writecounter']

__docformat__ = 'restructuredtext'

import os

class osplitter:
    """
    An output stream splitter.

    This class behaves like a writable file (with a `write` method),
    but the writing is redirected to other streams registered with the
    splitter. This behaviour is useful in scripts producing data on
    stdout and log messages on stderr, where one wants to output the
    log messages to both a file and to the console.

    This class also implements the context manager interface, so it
    can be used in conjunction with the `with` statement.
    
    """
    def __init__(self, *files):
        """
        Initialize and register all given `files`.
        """
        self._files = []
        self._opened_here = []
        for f in files:
            self.register(f)

    def _register_stream(self, f):
        """Abstracting away the stream registration"""
        self._files.append(f)

    def register(self, f, mode='w'):
        """
        Register `f` and return True if successful.

        If `f` supports the `write` method, `f` is considered a stream
        allready and immediately added.

        If `f` is a string, try to register the file object returned
        by `open(f,mode)` with `self`. No exceptions are caught, so
        `IOError`'s are propagated to the caller.

        Returns True if 'f' was successfully registered.
        """
        if hasattr(f, 'write'):
            self._register_stream(f)
            return True
        else:
            f = open(f, mode)
            self._register_stream(f)
            return True

    def __len__(self):
        """Returns the number of streams handled."""
        return len(self._files)

    def write(self, msg):
        """Propagate write call to all handled streams."""
        for f in self._files:
            f.write(msg)

    def close(self):
        """
        Closes all locally opened files.
        
        Locally opened files are the ones where only a file name was
        given as input to the constructor.
        """
        for f in self._opened_here:
            f.close()
        self._files = []
        self._opened_here = []

    def __enter__(self):
        """Returns self."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes self before returning False."""
        self.close()
        return False

class writecounter:
    
    """Class for counting the number of `write` calls.

        >>> counter = writecounter()
        >>> for i in range(3):
        ...     counter.write('bla bla bla')
        ...
        >>> counter.tell()
        3
        >>> counter.count
        3

    """
    
    def __init__(self, initial_value=0):
        """Initialize with an optional initial value."""
        self.count = initial_value
                
    def write(self, message):
        """Increase count by one.

        The `message` is never used.

        """
        self.count += 1

    def tell(self):
        """Returns the current count.

        Also available as the attribute `.count`.

        """
        return self.count
        

def _has_ext(filename, ext):
    fbase, fext = os.path.splitext(filename)
    return fext == ext

def fileswithext(args, ext):
    for fn in args:
        if _has_ext(fn, ext):
            yield fn

def getdatfiles(files, ext='.dat'):
    return [f for f in fileswithext(files, ext)]

def getlogfiles(files, ext='.log'):
    return [f for f in fileswithext(files, ext)]

if __name__=="__main__":
    import doctest
    doctest.testmod()
#     import sys
#     import os

#     files = [fn for fn in sys.argv[1:] if not os.path.exists(fn)]
#     datfiles = getdatfiles(files)
#     logfiles = getlogfiles(files)

#     # Redirect stdout both to file(s) and to stdout
#     stderr = multiplexer(*logfiles)
#     stderr.add_file(sys.stderr)

#     print >>stderr, "Output this message to the following files"
#     for fn in logfiles:
#         print >>stderr, fn

#     print "This was written to stdout"

