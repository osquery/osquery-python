import errno
import logging
import os
import socket
import sys
import win32pipe
import win32file
import win32api
import win32security

from thrift.transport.TTransport import TTransportBase
from thrift.transport.TTransport import TTransportException
from thrift.transport.TTransport import TServerTransportBase

logger = logging.getLogger(__name__)

INVALID_HANDLE_VALUE = 6
ERROR_PIPE_BUSY = 231

# TODO: What.. Do we need this?
class TPipeBase(TTransportBase):
    def __init__():
        pass

# Currently only supports named pipes :)
class TPipe(TPipeBase):
    """Pipe implementation of TTransport base."""

    def __init__(self, pipe, timeout=5):
        """Initialize a TPipe

        @param name(str)  The named pipe to connect to
        """
        self._pipe = pipe
        self._timeout = timeout
        self._handle = None

    def setHandle(self, h):
        self._handle = h

    def isOpen(self):
        return self._handle is not None

    @property
    def _pipe(self):
        return self._pipe

    def open(self):
        if self._handle != None:
            return
        handle = None
        try:
            while True:
                handle = win32file.CreateFile(self._pipe, win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, win32file.FILE_FLAG_OVERLAPPED | win32file.FILE_FLAG_WRITE_THROUGH, None)

                if handle.handle != INVALID_HANDLE_VALUE:
                    break

                err = win32api.GetLastError()
                if err != ERROR_PIPE_BUSY:
                    raise TTransportException(TTransportException.NOT_OPEN, "Failed to open connection to pipe: {}".format(err))

                # Wait for the connection to the pipe
                win32pipe.WaitNamedPipe(self._pipe, self._timeout * 1000)

        except Exception as e:
            raise TTransportException(TTransportException.NOT_OPEN, "Failed to open connection to pipe: {}".format(err))
        self._handle = handle
        return

    # TODO: GetOverlappedResult
    def read(self, sz):
        if not self.isOpen():
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='Called read on non-open pipe')

        buff = win32file.AllocateReadBuffer(sz)
        bytesRead = 0
        try:
            ret = win32file.ReadFile(self._handle, buff, None)
        except Exception as e:
            raise TTransportException(type=TTransportException.UNKNOWN,
                                      message='Failed to read from named pipe')
        print('[+] read: {}'.format(buff))
        return buff

    # TODO: GetOverlappedResult
    def write(self, buff):
        print('[+] write: {}'.format(buff))
        if not self._handle:
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='Transport not open')

        try:
            ret = win32file.WriteFile(self._handle, buff, None)
        except Exception as e:
            raise TTransportException(type=TTransportException.UNKNOWN,
                                      message='Failed to write to named pipe')

    def flush(self):
        pass

    def close(self):
        if self._handle != None:
            self._handle.close()
            win32pipe.DisconnectNamedPipe(self._pipe)
            self._handle = None


class TPipeServer(TPipeBase, TServerTransportBase):
    """Pipe implementation of TServerTransport base."""

    def __init__(self, pipe, buffsize=4096, maxconns=255):
        self._pipe = pipe
        self._buffsize = buffsize
        self._maxconns = maxconns
        self._handle = None

    def createNamedPipe(self):
        saAttr = win32security.SECURITY_ATTRIBUTES()
        saAttr.bInheritHandle = 0

        self._handle = win32pipe.CreateNamedPipe(self._pipe, win32pipe.PIPE_ACCESS_DUPLEX, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT, self._maxconns, self._buffsize, self._buffsize, 0, saAttr)

        err = win32api.GetLastError()
        if self._handle.handle == INVALID_HANDLE_VALUE:
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='TCreateNamedPipe failed: {}'.format(err))

    def initiateNamedConnect(self):
        if self._handle == None:
            self.createNamedPipe()

    def listen(self):
        pass

    def accept(self):
        if self._handle == None:
            self.createNamedPipe()
