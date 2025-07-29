# -*- coding: utf-8 -*-

import ast
import datetime
import errno
import logging
import os
import select
import socket
import time
import threading

from modules import module


logger = logging.getLogger(__name__)
DEFAULT_FILE = '/var/run/engine_listener'


class FileReader(module.Module):
    """Opens a file for reading and triggers actions"""

    def __init__(self, name, function_references):
        """Create a new instance of the class"""
        super().__init__(name, function_references)

    def get_filename(self):
        """Return the name of the event file"""
        return self.get_config('event_file', DEFAULT_FILE)

    def sleep(self, numseconds):
        """Wait interruptible"""
        for i in range(numseconds):
            time.sleep(1)
            if not self.is_Active:
                return

    def process_data(self, data):
        """Decode provided data and trigger action"""
        logger.debug('Processing data [{0}]'.format(data))
        # Example: [['exec_task', ['logic.set_default_config'], {}]]
        data = ast.literal_eval(data)
        logger.info('Processing data [{0}]'.format(data))
        for cmd in data:
            method_name, args, kwargs = cmd
            args_str = ', '.join(args)
            kwargs_str = ', '.join([str(k) + ': ' + str(v) for k, v in kwargs.items()])
            if len(args_str) and len(kwargs_str):
                args_str += ', '
            logger.info('Calling ' + method_name + '(' + args_str + kwargs_str + ')')
            method = getattr(self, method_name)
            return method(*args, **kwargs)

    def run(self):
        """Read lines from file and react on new lines"""
        fd = None
        ename = self.get_filename()
        data = bytearray('', encoding='utf-8')
        while self.Is_Active:
            try:
                if fd is None:
                    try:
                        fd = os.open(filename, os.O_RDONLY | os.O_NONBLOCK)
                    except Exception as e:
                        fd = None
                        logger.warning('File [{0}] could not be opened for reading: {1}; will try again in 30 seconds'.format(filename, e))
                        self.sleep(30)
                if fd is not None:
                    newdata = '[dummy]'
                    while newdata is not None:
                        try:
                            try:
                                newdata = None
                                # Note: The select works once but after the first read it returns immediately even if there is nothing more to read if the FIFO is not open for writing
                                # Thus we need to be able to cope with non-blocking behaviour of os.read
                                rrdy, wrdy, xrdy = select.select([fd], [], [], 1)  # select with 1 second timeout
                                if len(rrdy) > 0:
                                    newdata = os.read(fd, 2048)
                            except BlockingIOError:
                                newdata = None
                        except Exception as e:
                            newdata = None
                            logger.warning('Could not read from [{0}]: {1}; closing file and starting over'.format(filename, e))
                            os.close(fd)
                            fd = None
                        if (newdata is not None) and (len(newdata) == 0):
                            newdata = None
                        if newdata is not None:
                            data += newdata
                            sep = 'dummy'
                            while (len(sep) > 0):
                                part1, sep, part2 = data.partition(b'\n')
                                if len(sep) > 0:
                                    data = part2
                                    self.process_data(part1.decode('utf-8'))
            except Exception as e:
                # Print exceptions and log to file
                logger.critical('Exception occured: [{0}]'.format(e))
                logger.exception('Exception info:')  # just error but prints traceback
                #with open(EXCEPTION_PATH, 'a') as handle:
                #    handle.write(datetime.datetime.now().isoformat(sep = ' '));
                #    handle.write('\n');
                #    traceback.print_exc(file = handle);
                #    handle.write('\n');
            # Wait a moment
            if self.Is_Active:
                time.sleep(0.05)  # short time is a workaround: obviously, non-blocking call has the problem that the peer cannot fill the pipe

    def mkfifo(self, filename):
        """Creates a FIFO file"""
        try:
            os.mkfifo(filename, 0o640)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise()

    def run_config(self):
        """Starts the thread"""
        super().run_config()
        self.mkfifo(self.get_filename())
        logger.debug('Child thread starting')
        self.activate()
        self._thread = threading.Thread(target=self.run)
        self._thread.start()
        logger.debug('Child thread started')


module_class = FileReader
