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
import winerror
import pywintypes

from thrift.transport.TTransport import TTransportBase
from thrift.transport.TTransport import TTransportException
from thrift.transport.TTransport import TServerTransportBase


class TPipeBase(TTransportBase):
    """Base class for Windows TPipe transport"""

    def __init__(self):
        self._handle = None

    def close(self):
        """
        Generic close method, as both server and client rely on closing pipes
        in the same way
        """
        if self._handle is not None:
            win32pipe.DisconnectNamedPipe(self._handle)
            self._handle = None


class TPipe(TPipeBase):
    """Client for communicating over Named Pipes"""

    def __init__(self, pipeName, timeout=5, maxAttempts=5):
        """
        Initialize a TPipe client

        @param pipeName(string)  The path of the pipe to connect to.
        @param timeout(int)  The time to wait for a named pipe connection.
        @param maxAttempts(int)  Maximum number of connection attempts.
        """
        self._handle = None
        self._pipeName = pipeName
        self._timeout = timeout
        self._maxConnAttempts = maxAttempts

    def setHandle(self, h):
        self._handle = h

    def isOpen(self):
        return self._handle is not None

    def open(self):
        if self.isOpen():
            raise TTransportException(TTransportException.ALREADY_OPEN)

        h = None
        conns = 0
        while conns < self._maxConnAttempts:
            try:
                h = win32file.CreateFile(
                    self._pipeName,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE, 0, None,
                    win32file.OPEN_EXISTING, win32file.FILE_FLAG_OVERLAPPED,
                    None)
            except Exception as e:
                if e[0] != winerror.ERROR_PIPE_BUSY:
                    raise TTransportException(
                        TTransportException.NOT_OPEN,
                        'Failed to open connection to pipe: {}'.format(e))

            # Successfully connected, break out.
            if h is not None and h.handle != winerror.ERROR_INVALID_HANDLE:
                self._handle = h
                return

            # Wait for the connection to the pipe
            try:
                win32pipe.WaitNamedPipe(self._pipeName, self._timeout)
            except Exception as e:
                if e.args[0] not in (winerror.ERROR_SEM_TIMEOUT,
                                     winerror.ERROR_PIPE_BUSY):
                    raise TTransportException(
                        type=TTransportException.UNKNOWN,
                        message='Client failed to connect to server with {}'.
                        format(e.args[0]))
            conns += 1

        raise TTransportException(
            type=TTransportException.UNKNOWN,
            message='Client exceeded max connection attempts')

    def read(self, sz):
        if not self.isOpen():
            raise TTransportException(
                type=TTransportException.NOT_OPEN,
                message='Called read on non-open pipe')
        buff = None
        err = None
        try:
            (err, buff) = win32file.ReadFile(self._handle, sz, None)
        except Exception as e:
            raise TTransportException(
                type=TTransportException.UNKNOWN, message='TPipe read failed')

        if err != 0:
            raise TTransportException(
                type=TTransportException.UNKNOWN,
                message='TPipe read failed with GLE={}'.format(err))
        if len(buff) == 0:
            raise TTransportException(
                type=TTransportException.END_OF_FILE,
                message='TPipe read 0 bytes')
        return buff

    def write(self, buff):
        if not self.isOpen():
            raise TTransportException(
                type=TTransportException.NOT_OPEN,
                message='Called read on non-open pipe')

        bytesWritten = None
        try:
            (_, bytesWritten) = win32file.WriteFile(self._handle, buff, None)
        except Exception as e:
            raise TTransportException(
                type=TTransportException.UNKNOWN,
                message='Failed to write to named pipe: ' + e.message)

        if bytesWritten != len(buff):
            raise TTransportException(
                type=TTransportException.UNKNOWN,
                message='Failed to write complete buffer to named pipe')

    def flush(self):
        if self.isOpen():
            win32file.FlushFileBuffers(self._handle)


class TPipeServer(TPipeBase, TServerTransportBase):
    """Named pipe implementation of TServerTransport"""

    def __init__(self,
                 pipeName,
                 buffSize=4096,
                 maxConns=255,
                 maxConnAttempts=5):
        """
        Initialize a TPipe client

        @param pipeName(string)  The path of the pipe to connect to.
        @param buffSize(int)  The size of read/write buffers to use.
        @param maxConns(int)  Maximum number of simultaneous connections.
        @param maxConnAttempts(int)  Maximum number of connection attempts
        """
        self._pipeName = pipeName
        self._buffSize = buffSize
        self._maxConns = maxConns
        self._maxConnAttempts = maxConnAttempts
        self._handle = None

        # Overlapped event for Windows Async IO
        self._overlapped = pywintypes.OVERLAPPED()
        self._overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)

    # Create a new named pipe if one doesn't already exist
    def listen(self):
        if self._handle is None:
            self.createNamedPipe()

    def accept(self):
        if self._handle is None:
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
            self._pipeName, openMode, pipeMode,
            win32pipe.PIPE_UNLIMITED_INSTANCES, self._buffSize, self._buffSize,
            win32pipe.NMPWAIT_WAIT_FOREVER, saAttr)

        err = win32api.GetLastError()
        if self._handle.handle == winerror.ERROR_INVALID_HANDLE:
            raise TTransportException(
                type=TTransportException.NOT_OPEN,
                message='TCreateNamedPipe failed: {}'.format(err))
        return True

    def initiateNamedConnect(self):
        conns = 0
        while conns < self._maxConnAttempts:
            try:
                ret = win32pipe.ConnectNamedPipe(self._handle,
                                                 self._overlapped)
            except Exception as e:
                raise TTransportException(
                    type=TTransportException.NOT_OPEN,
                    message='TConnectNamedPipe failed: {}'.format(e.message))

            # Successfully connected, break out.
            if ret == winerror.ERROR_PIPE_CONNECTED:
                win32event.SetEvent(self._overlapped.hEvent)
                break
