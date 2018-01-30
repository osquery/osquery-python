"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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

INVALID_HANDLE_VALUE = 6
ERROR_PIPE_BUSY = 231

class TPipeBase(TTransportBase):
    def __init__():
        pass

    def close(self):
        if self._handle != None:
            win32pipe.DisconnectNamedPipe(self._handle)
            self._handle = None

class TPipe(TPipeBase):
    """Pipe implementation of TTransport base."""

    _pipeName = None
    _timeout = None
    _handle = None

    def __init__(self, pipeName, timeout=5):
        self._pipeName = pipeName
        self._timeout = timeout

    def setHandle(self, h):
        self._handle = h

    def isOpen(self):
        return self._handle is not None

    def open(self):
        if self.isOpen():
            raise TTransportException(TTransportException.ALREADY_OPEN)
        err = None
        h = None

        while True:
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
                                              'Failed to open connection to pipe: {}'.format(e))
            # Success, break out.
            if h != None and h.handle != INVALID_HANDLE_VALUE:
                break

            # Wait for the connection to the pipe
            try:
                #TODO: Set the timeout here to be the param passed in
                win32pipe.WaitNamedPipe(self._pipeName, self._timeout)
            except Exception as e:
                if e.args[0] not in (winerror.ERROR_SEM_TIMEOUT, winerror.ERROR_PIPE_BUSY):
                    raise TTransportException(type=TTransportException.UNKNOWN,
                                              message='Client failed to connect to server with {}'.format(e.args[0]))
        self._handle = h

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
        return buff

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

    def flush(self):
        win32file.FlushFileBuffers(self._handle)


class TPipeServer(TPipeBase, TServerTransportBase):
    """Pipe implementation of TServerTransport base."""

    def __init__(self, pipeName, buffsize=4096, maxconns=255):
        self._pipeName = pipeName
        self._buffsize = buffsize
        self._maxconns = maxconns
        self._handle = None

        # Overlapped event for Windows Async IO
        self._overlapped = pywintypes.OVERLAPPED()
        self._overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)

    # Create a new named pipe if one doesn't already exist
    def listen(self):
        if self._handle == None:
            ret = self.createNamedPipe()
        if ret != True:
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='TCreateNamedPipe failed')

    def accept(self):
        if self._handle == None:
            self.createNamedPipe()

        self.initiateNamedConnect()
        result = TPipe(self._pipeName)

        result.setHandle(self._handle)
        return result

    def createNamedPipe(self):
        openMode = win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED
        pipeMode = win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE

        saAttr = pywintypes.SECURITY_ATTRIBUTES()
        saAttr.SetSecurityDescriptorDacl(1, None, 0)

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
            return False
        return True

    def initiateNamedConnect(self):
        while True:
            try:
                ret = win32pipe.ConnectNamedPipe(self._handle, self._overlapped)
            except Exception as e:
                raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='TConnectNamedPipe failed: {}'.format(err))

            if ret == winerror.ERROR_PIPE_CONNECTED:
                win32event.SetEvent(self._overlapped.hEvent)
                break
