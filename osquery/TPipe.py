import errno
import logging
import os
import socket
import sys
import time

import win32event
import win32pipe
import win32file
import win32api
import win32security
import winerror
import pywintypes

from thrift.transport.TTransport import TTransportBase
from thrift.transport.TTransport import TTransportException
from thrift.transport.TTransport import TServerTransportBase

logger = logging.getLogger(__name__)

INVALID_HANDLE_VALUE = 6
ERROR_PIPE_BUSY = 231

pid = os.getpid()

class TPipeBase(TTransportBase):
    def __init__():
        print('[+] TPipeBase constructed')

    def close(self):
        print('[+] Close called')
        if self._handle != None:
            win32pipe.DisconnectNamedPipe(self._handle)
            self._handle = None

class TPipe(TPipeBase):
    """Pipe implementation of TTransport base."""

    _pipeName = None
    _timeout = None
    _handle = None

    def __init__(self, pipeName, timeout=5):
        """
        Initialize a TPipe

        @param name(str)  The named pipe to connect to
        """
        print('[+] TPipe client constructed [{}]'.format(os.getpid()))
        self._pipeName = pipeName
        self._timeout = timeout

    def setHandle(self, h):
        print('[+] handle set')
        self._handle = h

    def isOpen(self):
        print("[+] isOpen - {}".format(self._handle is not None))
        return self._handle is not None

    def open(self): 
        print('[+] Opening named pipe: {}'.format(self._pipeName))
        if self.isOpen():
            raise TTransportException(TTransportException.ALREADY_OPEN)
        err = None
        h = None

        while True:
            #print('[+] Attempting to open pipe: {}'.format(self._pipeName))
            try:
                h = win32file.CreateFile( self._pipeName,
                                        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                        0,
                                        None,
                                        win32file.OPEN_EXISTING,
                                        win32file.FILE_FLAG_OVERLAPPED,
                                        None)
            except Exception as e:
                if e[0] != ERROR_PIPE_BUSY:
                    raise TTransportException(TTransportException.NOT_OPEN,
                                              "Failed to open connection to pipe: {}".format(e))
            # Success, break out.
            if h != None and h.handle != INVALID_HANDLE_VALUE:
                print('[+] Handle received: {}'.format(h))
                print('[+] Handle received: {}'.format(h.handle))
                break
            err = win32api.GetLastError()
            print('[+] Client CreateFile GLE: {}, {}'.format(self._pipeName, err))

            # Wait for the connection to the pipe
            try:
                win32pipe.WaitNamedPipe(self._pipeName, 1000)
            except Exception as e:
                print e.args

        print('[+] Client [{}]: Client has connected to named pipe'.format(pid))
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
        print('[+] Read [{}]: {}'.format(len(buff), buff))
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
        print('[+] Write [{}]: {}'.format(bytesWritten, buff))

    def flush(self):
        print('[+] flush')
        win32file.FlushFileBuffers(self._handle)


class TPipeServer(TPipeBase, TServerTransportBase):
    """Pipe implementation of TServerTransport base."""

    def __init__(self, pipeName, buffsize=4096, maxconns=255, timeout=100):
        print('[+] TPipeServer server constructed [{}]'.format(os.getpid()))
        self._pipeName = pipeName
        self._buffsize = buffsize
        self._maxconns = maxconns
        self._handle = None
        self._timeout = timeout

        # Async file I/O overlapped event
        self._overlapped = pywintypes.OVERLAPPED()
        self._overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)

    # Listen in C++ code will reset the implementation handle to be a new
    # TNamedPipeServer instance, which in turn calls `initiateNamedConnect`
    def listen(self):
        print('[+] Listen called')
        #self.createNamedPipe()
        
        openMode = win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED
        pipeMode = win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE

        saAttr = pywintypes.SECURITY_ATTRIBUTES()
        saAttr.SetSecurityDescriptorDacl(1, None, 0)

        print('[+] Creating new named pipe')
        self._handle = win32pipe.CreateNamedPipe(
                        self._pipeName,
                        openMode,
                        pipeMode,
                        win32pipe.PIPE_UNLIMITED_INSTANCES,
                        self._buffsize,
                        self._buffsize,
                        win32pipe.NMPWAIT_WAIT_FOREVER,
                        saAttr)

        err = win32api.GetLastError()
        if self._handle.handle == INVALID_HANDLE_VALUE:
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='TCreateNamedPipe failed: {}'.format(err))

        while True:

            try:
                ret = win32pipe.ConnectNamedPipe(self._handle, self._overlapped)
            except Exception as e:
                raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='TConnectNamedPipe failed: {}'.format(err))
            
            # Success! Client has connected, signal the overlapped event
            if ret == winerror.ERROR_PIPE_CONNECTED:
                win32event.SetEvent(self._overlapped.hEvent)
                break
        
        print('[+] Server [{}]: Server has connected to named pipe'.format(pid))




    # Mimicking the TSocket implementations, not sure if this'll work
    def accept(self):
        print('[+] Accept called')
        #gle = self.connectPipe()

        #print('[+] ConnectNamedPipe GLE: [{}]'.format(gle))
        result = TPipe(self._pipeName)
        #print('[+] HANDLE: {}'.format(self._handle.handle))
        #print('[+] PIPE: {}'.format(self._pipeName))
        result.open()

        result.setHandle(self._handle)
        return result
