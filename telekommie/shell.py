""" Telekommunisten Integration Environment 
    Shell Accoess Objects

    Dmytri Kleiner <dk@telekommunisten.net>
"""

from subprocess import PIPE, STDOUT, Popen, call

class ShellAccessObject():
    """ Provides access methods to shell subprocesses
        with environment variable injection
    """
    def __init__(self):
        self.env = None

    class Errors:
        class CommandFailed(Exception):
            def __init__(self, command, err, code):
                self.command = command
                self.err = err
                self.code = code
            def __str__(self):
                return "Command %s failed: %s (%s)" % \
                        (self.command, self.err, self.code)
    def setEnv(self, key, value):
        """ Set environment variable

            >>> s = ShellAccessObject()
            >>> s.setEnv("TEST", "TESTING")
            >>> s.env["TEST"]
            'TESTING'
        """
        if None == self.env:
            import os
            self.env = os.environ.copy()
        self.env[key] = value
    def access(self, command):
        """ Execute shell command and return response

            >>> s = ShellAccessObject()
            >>> command = ["echo","TESTING"]
            >>> s.access(command)
            'TESTING'
        """
        sub = Popen(command, env=self.env, stdout=PIPE, stderr=STDOUT)
        response = sub.communicate()[0].strip()
        if sub.returncode:
            raise self.Errors.CommandFailed(str(command),
                    sub.stderr,
                    sub.returncode)
        return response

