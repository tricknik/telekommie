from hooks import Hooks
from git_tests import FakeGitAccessObject
import unittest

class TestHooks(unittest.TestCase):

    def setUp(self, methodName="runTest"):
        self.git = FakeGitAccessObject()

    # Test Errors

    def testRefDisallowed(self):
        try:
            raise Hooks.Errors.RefDisallowed("error")
        except Hooks.Errors.RefDisallowed as e:
            self.assertTrue(str(e)) 
    def testCommitterMismatch(self):
        try:
            raise Hooks.Errors.CommitterMismatch("error")
        except Hooks.Errors.CommitterMismatch as e:
            self.assertTrue(str(e)) 
    def testTaggingFailed(self):
        try:
            raise Hooks.Errors.TaggingFailed("error", "error")
        except Hooks.Errors.TaggingFailed as e:
            self.assertTrue(str(e)) 

    # Test Hooks

    def testUpdate(self):
        """ Telekommie should allow pushing to a new branch
        """
        self.git.setAccessResponse('Dmytri Kleiner')
        Hooks.update("refs/heads/newbranch","A" * 40, "F" * 40, self.git)
    def testUpdateMaster(self):
        """ Telekommie should not allow pushing to master
        """
        def tryToUpdateMaster():
            Hooks.update("refs/heads/master","0" * 40, "0" * 40)
        self.assertRaises(Hooks.Errors.RefDisallowed, tryToUpdateMaster)
    def testUpdateTag(self):
        """ Telekommie should not allow pushing to a tag
        """
        def tryToUpdateTag():
            Hooks.update("tags/init","0" * 40, "0" * 40)
        self.assertRaises(Hooks.Errors.RefDisallowed, tryToUpdateTag)
    def testChangeCommitter(self):
        """ Telekommie should not allow changing the commiter of a branch
        """
        def tryToChangeCommitter(self=self):
            from git_tests import FakeGitAccessObject
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

