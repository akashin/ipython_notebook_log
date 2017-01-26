import sys
import os

from io import StringIO

from IPython.core.magic import (Magics, magics_class, line_magic)

_ORIGINAL_STDOUT = sys.stdout
_ORIGINAL_STDERR = sys.stderr


def save_data(ip, key, value):
    if "kv_storage" not in dir(ip):
        ip.kv_storage = {}
    ip.kv_storage[key] = value


def get_data(ip, key):
    if "kv_storage" not in dir(ip):
        return None
    return ip.kv_storage.get(key, None)


@magics_class
class LoggingMagics(Magics):
    @line_magic
    def register_logging(self, line):
        ip = self.shell

        logging_started = get_data(ip, "logging_started")
        if logging_started:
            print(" Logging is already active")
            return

        from time import strftime
        import os.path
        filepath = line
        if filepath.startswith("~"):
            filepath = os.path.expanduser(filepath)
        filename = os.path.basename(filepath)
        notnew = os.path.exists(filepath)

        try:
            capture_print(filepath)
            ip.magic('logstart -o %s append' % filepath)
            if notnew:
                ip.logger.log_write(u"# =================================\n")
            else:
                ip.logger.log_write(u"#!/usr/bin/env python\n")
                ip.logger.log_write(u"# " + filename + "\n")
                ip.logger.log_write(u"# IPython automatic logging file\n")
            ip.logger.log_write(u"# " + strftime('%H:%M:%S') + "\n")
            ip.logger.log_write(u"# =================================\n")

            output_framer = OutputFramer(ip)
            ip.events.register('pre_execute', output_framer.pre_execute)
            ip.events.register('post_execute', output_framer.post_execute)
            save_data(ip, "output_framer", output_framer)

            save_data(ip, "logging_started", True)

            print(" Logging to " + filepath)
        except RuntimeError:
            print(" Already logging to " + ip.logger.logfname)


class OutputFramer(object):
    def __init__(self, ip):
        self.shell = ip

    def pre_execute(self):
        pass

    def post_execute(self):
        self.shell.logger.log_write(u"\n")
        self.shell.logger.log_write(u"######################\n")
        self.shell.logger.log_write(u"\n")


def load_ipython_extension(ip):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.
    ip.register_magics(LoggingMagics)


def unload_ipython_extension(ip):
    stop_capturing_print()
    ip.magic('logstop')
    output_framer = get_data(ip, "output_framer")
    if output_framer is not None:
        ip.events.unregister('pre_execute', output_framer.pre_execute)
        ip.events.unregister('post_execute', output_framer.post_execute)
        save_data(ip, "output_framer", None)
    save_data(ip, "logging_started", False)

class CaptureStdOut(object):
    """
    An logger that both prints to stdout and writes to file.
    """

    def __init__(self, log_file_path=None, print_to_console=True):
        """
        :param log_file_path: The path to save the records,
               or None if you just want to keep it in memory
        :param print_to_console:
        """
        self._print_to_console = print_to_console
        if log_file_path is not None:
            dirpath = os.path.dirname(log_file_path)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            self.log = open(log_file_path, 'a')
        else:
            self.log = StringIO()
        self._log_file_path = log_file_path
        self.terminal = _ORIGINAL_STDOUT

    def __enter__(self):
        sys.stdout = self
        sys.stderr = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = _ORIGINAL_STDOUT
        sys.stderr = _ORIGINAL_STDERR
        self.close()

    def write(self, message):
        if self._print_to_console:
            self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def close(self):
        if self._log_file_path is not None:
            self.log.close()

    def read(self):
        if self._log_file_path is None:
            return self.log.getvalue()
        else:
            with open(self._log_file_path) as f:
                txt = f.read()
            return txt

    def __getattr__(self, item):
        return getattr(self.terminal, item)


def capture_print(log_file_path, print_to_console=True):
    """
    :param log_file_path: Path of file to print to, if (state and to_file).
        If path does not start with a "/", it will
        be relative to the data directory.  You can use placeholders
        such as %T, %R, ... in the path name (see format filename)
    :param print_to_console:
    :param print_to_console: Also continue printing to console.
    :return: The absolute path to the log file.
    """
    local_log_file_path = log_file_path
    logger = CaptureStdOut(log_file_path=local_log_file_path, print_to_console=print_to_console)
    logger.__enter__()
    sys.stdout = logger
    sys.stderr = logger
    return local_log_file_path


def stop_capturing_print():
    sys.stdout = _ORIGINAL_STDOUT
    sys.stderr = _ORIGINAL_STDERR
