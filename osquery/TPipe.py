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

# TODO: Is there anything needed here? What about having `close` be a member
# of the parent function
class TPipeBase(TTransportBase):
    def __init__():
        pass

    def close(self):
        print('[+] Close called')
        if self._handle != None:
            win32pipe.DisconnectNamedPipe(self._pipe)
            win32file.CloseHandle(self._handle)
            self._handle = None

class TPipe(TPipeBase):
    """Pipe implementation of TTransport base."""

    _pipe = None
    _timeout = None
    _handle = None

    def __init__(self, pipe, timeout=5):
        """
        Initialize a TPipe

        @param name(str)  The named pipe to connect to
        """
        print('[+] client constructed')
        self._handle = None
        self._pipe = pipe
        self._timeout = timeout

    def setHandle(self, h):
        print('[+] handle set')
        self._handle = h

    def isOpen(self):
        print('[+] checking if isOpen')
        return self._handle is not None

    def open(self):
        print('[+] Opening named pipe: {}'.format(self._pipe))
        if self._handle:
            raise TTransportException(TTransportException.ALREADY_OPEN)
        err = None
        h = None
        try:
            while True:
                h = win32file.CreateFile( self._pipe,
                                        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                        0,
                                        None,
                                        win32file.OPEN_EXISTING,
                                        win32file.FILE_FLAG_OVERLAPPED,
                                        None)

                if h.handle != INVALID_HANDLE_VALUE:
                    break

                err = win32api.GetLastError()
                if err != ERROR_PIPE_BUSY:
                    raise TTransportException(TTransportException.NOT_OPEN,
                                              "Failed to open connection to named pipe: {}".format(err))

                # Wait for the connection to the pipe
                win32pipe.WaitNamedPipe(self._pipe, self._timeout * 1000)

        except Exception as e:
            raise TTransportException(TTransportException.NOT_OPEN,
                                      "Failed to open connection to pipe: {}".format(err))
        self._handle = h


    # TODO: GetOverlappedResult
    def read(self, sz):
        if not self.isOpen():
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='Called read on non-open pipe')
        buff = None
        err = None
        try:
            (err, buff) = win32file.ReadFile(self._handle, sz, None)
        except Exception as e:
            raise TTransportException(type=TTransportException.UNKNOWN,
                                      message='TPipe read failed')

        if(err != 0):
            raise TTransportException(type=TTransportException.UNKNOWN,
                                      message='TPipe read failed with GLE={}'.format(err))
        if len(buff) == 0:
            raise TTransportException(type=TTransportException.END_OF_FILE,
                                      message='TPipe read 0 bytes')
        print('[+] read[{}]: {}'.format(len(buff), buff))
        return buff

    # TODO: GetOverlappedResult
    def write(self, buff):
        if not self.isOpen():
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='Called read on non-open pipe')
        err = None
        bytesWritten = None
        try:
            (writeError, bytesWritten) = win32file.WriteFile(self._handle, buff, None)
        except Exception as e:
            raise TTransportException(type=TTransportException.UNKNOWN,
                                      message='Failed to write to named pipe: ' + e.message)
        print('[+] wrote[{}]: {}'.format(bytesWritten, buff))

    def flush(self):
        print('[+] flush')
        win32file.FlushFileBuffers(self._handle)


class TPipeServer(TPipeBase, TServerTransportBase):
    """Pipe implementation of TServerTransport base."""

    def __init__(self, pipe, buffsize=4096, maxconns=255):
        self._pipe = pipe
        self._buffsize = buffsize
        self._maxconns = maxconns
        self._handle = None
        #self.initiateNamedConnect()

    def createNamedPipe(self):

        print('[+] Creating new named pipe')
        saAttr = win32security.SECURITY_ATTRIBUTES()
        saAttr.bInheritHandle = 0

        self._handle = win32pipe.CreateNamedPipe(
                        self._pipe,
                        win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED,
                        win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE,
                        self._maxconns,
                        self._buffsize,
                        self._buffsize,
                        win32pipe.NMPWAIT_WAIT_FOREVER,
                        saAttr)

        err = win32api.GetLastError()
        if self._handle.handle == INVALID_HANDLE_VALUE:
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='TCreateNamedPipe failed: {}'.format(err))

    def initiateNamedConnect(self):
        print('[+] initiateNamedConnect called')
        if self._handle == None:
            self.createNamedPipe()
            win32pipe.ConnectNamedPipe(self._handle, None)

    # Listen in C++ code will reset the implementation handle to be a new
    # TNamedPipeServer instance, which in turn calls `initiateNamedConnect`
    def listen(self):
        print('[+] Listen called')
        self.createNamedPipe()

    # Mimicking the TSocket implementations, not sure if this'll work
    def accept(self):
        print('[+] Accept called')
        self.initiateNamedConnect()
        result = TPipe(self._pipe)
        result.open()
        return result
