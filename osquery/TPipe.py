import errno
import logging
import os
import socket
import sys
import win32pipe
import win32file
import win32api

from thrift.transport.TTransport import TTransportBase, TTransportException, TServerTransportBase

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
        x = ''
        try:
            while True:
                handle = win32file.CreateFile(self._pipe, win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, win32file.FILE_FLAG_OVERLAPPED | win32file.FILE_FLAG_WRITE_THROUGH, None)

                print('A6')
                if handle.handle != INVALID_HANDLE_VALUE:
                    print('A7')
                    break

                err = win32api.GetLastError()
                if err != ERROR_PIPE_BUSY:
                    print('A8')
                    raise TTransportException(TTransportException.NOT_OPEN, "Failed to open connection to pipe: {}".format(err))

                # Wait for the connection to the pipe
                print('A3')
                win32pipe.WaitNamedPipe(self._pipe, self._timeout * 1000)
                print('A4')

        except Exception as e:
            print('A8')
            print('[-] Failed to connect to pipe: {}'.format(e))
            raise TTransportException(TTransportException.NOT_OPEN, "Failed to open connection to pipe: {}".format(err))
        print('E')
        self._handle = handle
        return

    # TODO: GetOverlappedResult
    def read(self, sz):
        if not isOpen():
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='Called read on non-open pipe')

        buff = win32file.AllocateReadBuffer(sz)
        bytesRead = 0
        try:
            ret = win32file.ReadFile(self._handle, buff, None)
        except Exception as e:
            raise TTransportException(type=TTransportException.UNKNOWN,
                                      message='Failed to read from named pipe')
        return buff

    # TODO: GetOverlappedResult
    def write(self, buff):
        if not self.handle:
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
