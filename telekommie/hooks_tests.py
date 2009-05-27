from hooks import Hooks
from git_tests import FakeGitAccessObject
import unittest

class TestHooks(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(TestHooks, self).__init__(methodName)
        self.git = FakeGitAccessObject()
    def testUpdateMaster(self):
        """ Telekommie should not allow pushing to master
        """
        def tryToUpdateMaster():
            Hooks.update("master","0" * 40, "0" * 40, self.git)
        self.assertRaises(Hooks.Errors.RefDisallowed, tryToUpdateMaster)
    def testUpdateTag(self):
        """ Telekommie should not allow pushing to a tag
        """
        def tryToUpdateTag():
            Hooks.update("tags/init","0" * 40, "0" * 40, self.git)
        self.assertRaises(Hooks.Errors.RefDisallowed, tryToUpdateTag)
    def testChangeCommitter(self):
        """ Telekommie should not allow changing the commiter of a branch
        """
        def tryToChangeCommitter(self=self):
            from git import FakeGitAccessObject
            fakeShow = \
"""
Monty Cantsin
diff --git a/NEOISM b/NEOISM
new file mode 100644
index 0000000..6666666
"""
            self.git.setAccessResponse(fakeShow)
            head = self.git.getCommit("0"*40)
            other = FakeGitAccessObject()
            fakeShow = \
"""
Dmytri Kleiner
diff --git a/README b/README
new file mode 100644
index 0000000..4337545
"""
            other.setAccessResponse(fakeShow)
            update = other.getCommit("0"*40)
            Hooks.haveMatchingCommitterNames(head, update)
            self.assertRaises(Hooks.Errors.CommitterMismatch, tryToChangeCommitter)

