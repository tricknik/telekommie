from shell import ShellAccessObject
import unittest

class Tests(unittest.TestCase):
    def setUp(self):
        self.shell = ShellAccessObject()

    # Error Tests

    def testCommandFailed(self):
        try:
            raise ShellAccessObject.Errors.CommandFailed("cmd","err",1)
        except ShellAccessObject.Errors.CommandFailed as e:
            self.assertTrue(str(e)) 

    # ShellAccessObject Tests

    def testSetEnv(self):
        self.shell.setEnv("TEST", "TESTING")
        self.assertEqual(self.shell.env["TEST"], 'TESTING')
    def testAccess(self): 
        self.assertEqual(self.shell.access(["echo","TESTING"]), 'TESTING')
        def tryFindBadCommand():
            self.shell.access(["which", "NOSUCHCOMMAND"])
        self.assertRaises(ShellAccessObject.Errors.CommandFailed, tryFindBadCommand)
        def tryBadCommand():
            self.shell.access(["NOSUCHCOMMAND"])
        self.assertRaises(OSError, tryBadCommand)



